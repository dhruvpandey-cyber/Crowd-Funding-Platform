from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
	fieldsets = UserAdmin.fieldsets + (
		(
			"Crowdfunding Info",
			{"fields": ("role", "phone_number", "is_creator_verified")},
		),
	)
	list_display = ("username", "email", "role", "is_creator_verified", "is_staff")

# Register your models here.
