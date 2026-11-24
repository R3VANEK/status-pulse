from dataclasses import dataclass
from pathlib import PurePosixPath

from projects.domain.exceptions import InvalidProjectAttachmentException

MAX_ATTACHMENT_FILE_SIZE_BYTES = 5 * 1024 * 1024
MAX_ATTACHMENT_FILE_NAME_LENGTH = 100
ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".doc",
    ".docx",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
    ".svg",
}


@dataclass(frozen=True, slots=True)
class AttachmentFile:
    name: str
    content: bytes
    content_type: str
    content_size: int

    def __post_init__(self) -> None:
        name = self.name.strip()

        if not name:
            raise InvalidProjectAttachmentException("file name cannot be empty.")

        if len(name) > MAX_ATTACHMENT_FILE_NAME_LENGTH:
            raise InvalidProjectAttachmentException(
                f"file name must be at most {MAX_ATTACHMENT_FILE_NAME_LENGTH} characters."
            )

        if "/" in name or "\\" in name:
            raise InvalidProjectAttachmentException("file name cannot contain slashes.")

        extension = PurePosixPath(name).suffix.lower()
        if extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
            allowed = ", ".join(sorted(ALLOWED_ATTACHMENT_EXTENSIONS))
            raise InvalidProjectAttachmentException(
                f"file type '{extension or '<none>'}' is not allowed. Allowed extensions: {allowed}."
            )

        if self.content_size > MAX_ATTACHMENT_FILE_SIZE_BYTES:
            raise InvalidProjectAttachmentException("file size must be at most 5MB.")

        if self.content_size < 0:
            raise InvalidProjectAttachmentException("file size cannot be negative.")

        object.__setattr__(self, "name", name)
