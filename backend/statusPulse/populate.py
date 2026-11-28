import os
import django
from botocore.exceptions import ClientError
import random
from uuid import uuid4
from typing import Any

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "statusPulse.settings")
django.setup()

from projects.infrastructure.factories import (
    ProjectFactory,
    ProjectAttachmentFactory,
)  # noqa: E402
from integrations.s3 import get_s3_client  # noqa: E402
from django.conf import settings  # noqa: E402
from accounts.infrastructure.models import User  # noqa: E402
from projects.infrastructure.models import Project, ProjectMembership  # noqa: E402
from django.core.files.uploadedfile import SimpleUploadedFile  # noqa: E402
from django.contrib.auth.models import Group, Permission  # noqa: E402
from django.db import transaction
from projects.infrastructure.factories import ProjectMembershipFactory
from accounts.infrastructure.factories import UserFactory

NO_ATTACHMENT_PER_PROJECT = (0, 4)
NO_USERS_PER_PROJECT = (1, 4)


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


def populate_users() -> None:
    print("----------------------------------------------------------")

    student_group = Group.objects.create(name="Student")
    student_permissions = Permission.objects.filter(
        name__in=[
            "Can add project attachment",
            "Can delete project attachment",
            "Can view project attachment",
            "Can view project",
        ]
    )
    student_group.permissions.add(*student_permissions)

    supervisor_group = Group.objects.create(name="Supervisor")
    supervisor_permissions = Permission.objects.filter(
        name__in=[
            "Can add new person to the project",
            "Can delete project",
            "Can change project",
            "Can add project attachment",
            "Can view project",
        ]
    )
    supervisor_group.permissions.add(*supervisor_permissions)

    no_created_users = 0


    memberships = []

    print("Creating project members...")

    for project in Project.objects.all():

        no_users = random.randint(*NO_USERS_PER_PROJECT)
        for i in range(no_users):
                user = UserFactory()

                group = (
                    supervisor_group
                    if i == 0
                    else random.choice([student_group, supervisor_group])
                )

                user.groups.add(group)

                memberships.append(
                    ProjectMembership(
                        user=user,
                        project=project,
                        group=group,
                    )
                )

    ProjectMembership.objects.bulk_create(memberships)

    no_created_users = len(memberships)

    print(f"Created groups and {no_created_users} users")




def populate_db() -> None:
    print("----------------------------------------------------------")

    admin = User(
        email=settings.ADMIN_EMAIL,
        username="admin",
        first_name="admin",
        surname="admin",
        is_staff=True,
        is_superuser=True,
        phone_number="531420609",
    )

    admin.set_password(settings.ADMIN_PASSWORD)
    admin.save()

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
    print("Created 50 projects.")
    print(f"Created {created_project_attachments} project attachments.")


if __name__ == "__main__":

    with transaction.atomic():
        populate_s3()
        populate_db()
        populate_users()
