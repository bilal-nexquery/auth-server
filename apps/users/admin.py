from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from apps.users.models import User


# Register your models here.
class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "username",
    )
    search_fields = ("email",)
    ordering = ("-id",)

    # fields defined in fieldset are shown in update user form
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    # fields defined in add_fieldsets are shown in create user form
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "username",
                ),
            },
        ),
    )


admin.site.unregister(Group)

admin.site.register(User, CustomUserAdmin)
