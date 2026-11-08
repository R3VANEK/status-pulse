import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "statusPulse.settings")
django.setup()

from demo.factories import ProgramFactory  # noqa: E402
from projects.infrastructure.factories import ProjectFactory  # noqa: E402

ProgramFactory.create_batch(50)
ProjectFactory.create_batch(50)

print("Created 50 programs.")
print("Created 50 projects.")
