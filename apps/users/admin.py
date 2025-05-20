from django.contrib import admin
from .models import EmailVerification, Profile
# Register your models here.

admin.site.register(EmailVerification)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'joined_at']
    readonly_fields = ['joined_at']
