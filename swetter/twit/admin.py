from django.contrib import admin
from .models import twit, Profile
# Register your models here.


@admin.register(twit)
class TwitAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_user_id', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')

    def get_user_id(self, obj):
        return obj.user.id
    get_user_id.short_description = 'User ID'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_user_id')
    search_fields = ('user__username', 'user__email')

    def get_user_id(self, obj):
        return obj.user.id
    get_user_id.short_description = 'User ID'