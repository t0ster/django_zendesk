# -*- coding: utf-8 -*-
import re

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


def validate_rater_id(value):
    # Matches any 4-digit number:
    rater = re.compile(r"^\d{4,7}$")

    # If year does not match our regex:
    if not rater.match(str(value)):
        msg = "%s should be between 4 and 7 digits Rater ID in the form of XXXXXXX."
        raise ValidationError(msg % value)


class User(AbstractUser):
    """Axis-customized User model."""

    company = models.ForeignKey(
        "company.Company", related_name="users", blank=True, null=True, on_delete=models.SET_NULL
    )

    is_company_admin = models.BooleanField(default=False)
