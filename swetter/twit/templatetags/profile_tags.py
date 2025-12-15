from django import template
from twit.models import Profile

register = template.Library()

@register.simple_tag
def get_profile(user):
    return Profile.objects.filter(user=user).first()