from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
	class Role(models.TextChoices):
		BACKER = "BACKER", "Backer"
		CREATOR = "CREATOR", "Creator"
		ADMIN = "ADMIN", "Admin"

	role = models.CharField(max_length=20, choices=Role.choices, default=Role.BACKER)
	phone_number = models.CharField(max_length=20, blank=True)
	is_creator_verified = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.username} ({self.role})"
