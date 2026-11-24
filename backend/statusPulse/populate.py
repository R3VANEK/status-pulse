import os
import django
from botocore.exceptions import ClientError
import random
from uuid import uuid4

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "statusPulse.settings")
django.setup()

from demo.factories import ProgramFactory  # noqa: E402
from projects.infrastructure.factories import ProjectFactory, ProjectAttachmentFactory  # noqa: E402
from integrations.s3 import get_s3_client  # noqa: E402
from django.conf import settings  # noqa: E402
from accounts.infrastructure.models import User  # noqa: E402
from projects.infrastructure.models import Project # noqa: E402
from django.core.files.uploadedfile import SimpleUploadedFile # noqa: E402


NO_ATTACHMENT_PER_PROJECT = (0, 4)


def populate_s3() -> None:

    print("----------------------------------------------------------")
    s3 = get_s3_client()

    desired_bucket_names = frozenset(
        [
            settings.S3_PROJECT_ATTACHMENT_BUCKET_NAME,
            settings.S3_TASK_ATTACHMENT_BUCKET_NAME,
        ]
    )

    for bucket in s3.client.list_buckets()["Buckets"]:
        bucket_name = bucket["Name"]
        deleted_objs_count = s3.delete_all_objects(bucket_name)
        s3.client.delete_bucket(Bucket=bucket_name)
        print(f"deleted bucket {bucket_name} with {deleted_objs_count} objects")

    for bucket in desired_bucket_names:
        try:
            s3.client.create_bucket(Bucket=bucket)
            print(f"created bucket {bucket}")
        except ClientError as error:
            print(f"Couldn't create s3 bucket '{bucket}', exc: {error}")


def populate_db() -> None:
    print("----------------------------------------------------------")

    admin = User(
        email=settings.ADMIN_EMAIL,
        username="admin",
        first_name="admin",
        surname="admin",
        is_staff=True,
        is_superuser=True,
    )

    admin.set_password(settings.ADMIN_PASSWORD)
    admin.save()

    ProgramFactory.create_batch(50)
    ProjectFactory.create_batch(50)

    created_project_attachments = 0

    for project in Project.objects.all():
        for _ in range(random.randrange(*NO_ATTACHMENT_PER_PROJECT)):
            created_project_attachments += 1
            ProjectAttachmentFactory(
                save_to_s3=True,
                project=project,
                file=SimpleUploadedFile(
                    name=f"mocked-{str(uuid4())[:4]}.txt",
                    content_type="text/plain",
                    content=b"hello there general kenobi",
                ),
            )

    print(f"Created admin {admin.email}")
    print("Created 50 programs.")
    print("Created 50 projects.")
    print(f"Created {created_project_attachments} project attachments.")


if __name__ == "__main__":
    populate_s3()
    populate_db()
