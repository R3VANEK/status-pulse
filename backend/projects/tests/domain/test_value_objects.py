from django.test import SimpleTestCase

from projects.domain.exceptions import InvalidProjectAttachmentException
from projects.domain.value_objects import (
    MAX_ATTACHMENT_FILE_NAME_LENGTH,
    MAX_ATTACHMENT_FILE_SIZE_BYTES,
    AttachmentFile,
)


class AttachmentFileTests(SimpleTestCase):
    def test_accepts_allowed_file(self) -> None:
        attachment = AttachmentFile(
            name="report.pdf",
            content=b"pdf-content",
            content_type="application/pdf",
            content_size=len(b"pdf-content"),
        )

        self.assertEqual(attachment.name, "report.pdf")

    def test_rejects_disallowed_extension(self) -> None:
        with self.assertRaisesMessage(
            InvalidProjectAttachmentException,
            "Invalid project attachment: file type '.exe' is not allowed.",
        ):
            AttachmentFile(
                name="malware.exe",
                content=b"MZ",
                content_type="application/octet-stream",
                content_size=2,
            )

    def test_rejects_file_over_max_size(self) -> None:
        with self.assertRaisesMessage(
            InvalidProjectAttachmentException,
            "Invalid project attachment: file size must be at most 5MB.",
        ):
            AttachmentFile(
                name="big.pdf",
                content=b"a" * (MAX_ATTACHMENT_FILE_SIZE_BYTES + 1),
                content_type="application/pdf",
                content_size=MAX_ATTACHMENT_FILE_SIZE_BYTES + 1,
            )

    def test_accepts_file_at_max_size(self) -> None:
        attachment = AttachmentFile(
            name="limit.pdf",
            content=b"",
            content_type="application/pdf",
            content_size=MAX_ATTACHMENT_FILE_SIZE_BYTES,
        )

        self.assertEqual(attachment.content_size, MAX_ATTACHMENT_FILE_SIZE_BYTES)

    def test_rejects_slashes_in_name(self) -> None:
        for name in ["../secret.pdf", "..\\secret.pdf", "folder/file.pdf"]:
            with self.subTest(name=name):
                with self.assertRaisesMessage(
                    InvalidProjectAttachmentException,
                    "Invalid project attachment: file name cannot contain slashes.",
                ):
                    AttachmentFile(
                        name=name,
                        content=b"content",
                        content_type="application/pdf",
                        content_size=7,
                    )

    def test_rejects_file_name_longer_than_100_characters(self) -> None:
        long_name = "a" * (MAX_ATTACHMENT_FILE_NAME_LENGTH - 3) + ".pdf"
        self.assertGreater(len(long_name), MAX_ATTACHMENT_FILE_NAME_LENGTH)

        with self.assertRaisesMessage(
            InvalidProjectAttachmentException,
            "Invalid project attachment: file name must be at most 100 characters.",
        ):
            AttachmentFile(
                name=long_name,
                content=b"content",
                content_type="application/pdf",
                content_size=7,
            )

    def test_accepts_file_name_with_100_characters(self) -> None:
        name = "a" * (MAX_ATTACHMENT_FILE_NAME_LENGTH - 4) + ".pdf"
        self.assertEqual(len(name), MAX_ATTACHMENT_FILE_NAME_LENGTH)

        attachment = AttachmentFile(
            name=name,
            content=b"content",
            content_type="application/pdf",
            content_size=7,
        )

        self.assertEqual(attachment.name, name)

    def test_accepts_supported_types_case_insensitively(self) -> None:
        for name in ["notes.TXT", "doc.DOCX", "image.JPEG"]:
            with self.subTest(name=name):
                attachment = AttachmentFile(
                    name=name,
                    content=b"content",
                    content_type="application/octet-stream",
                    content_size=7,
                )
                self.assertEqual(attachment.name, name)
