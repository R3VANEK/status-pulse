# Django discovers models only in "<app>/models.py".
# The real model lives in the infrastructure layer (DDD), we just re-export it here.
from accounts.infrastructure.models import User

__all__ = ["User"]
