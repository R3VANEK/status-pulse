import socket
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from botocore.exceptions import ClientError
from django.conf import settings
from django.test import SimpleTestCase

from integrations.s3 import get_s3_client


class S3StorageIntegrationTests(SimpleTestCase):
    bucket_name: str
    file_name: str
    file_content: bytes

    def setUp(self) -> None:
        self.storage = get_s3_client()
        self.bucket_name = f"status-pulse-test-{uuid4().hex}"
        self.file_name = "sample.txt"
        self.file_content = b"status-pulse s3 integration test\n"
        self._assert_storage_is_reachable()
        self.storage.client.create_bucket(Bucket=self.bucket_name)

    def tearDown(self) -> None:
        try:
            self.storage.delete_all_objects(self.bucket_name)
            self.storage.client.delete_bucket(Bucket=self.bucket_name)
        except ClientError:
            pass

    def _assert_storage_is_reachable(self) -> None:
        endpoint = settings.S3_ENDPOINT_URL
        parsed = urlparse(endpoint)
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        try:
            with socket.create_connection((host, port), timeout=5):
                pass
        except OSError as error:
            self.fail(
                f"S3 endpoint {endpoint} is not reachable ({error}). "
                "Start the storage with "
                "`docker compose -f docker-compose.test.yaml up -d s3`."
            )

    def _write_file(self) -> str:
        """Writes the test file to disk and returns its path."""
        directory = tempfile.mkdtemp()
        path = Path(directory) / self.file_name
        path.write_bytes(self.file_content)
        return str(path)

    def test_storage_is_running_and_lists_buckets(self) -> None:
        response = self.storage.client.list_buckets()

        bucket_names = [bucket["Name"] for bucket in response["Buckets"]]

        self.assertIn(self.bucket_name, bucket_names)

    def test_file_is_uploaded_and_downloaded_back(self) -> None:
        source = self._write_file()

        self.storage.client.upload_file(source, self.bucket_name, self.file_name)

        with tempfile.TemporaryDirectory() as directory:
            downloaded = Path(directory) / "downloaded.txt"
            self.storage.client.download_file(
                self.bucket_name, self.file_name, str(downloaded)
            )

            self.assertEqual(downloaded.read_bytes(), self.file_content)
