from django.db import models
from django.contrib.auth.models import User
import uuid





# Create your models here.

class twit(models.Model):

    user =models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=250)
    photo= models.ImageField(upload_to='photos/', blank=True, null=True)
    created_at= models.DateTimeField( auto_now_add=True)
    updated_at= models.DateTimeField( auto_now=True)


def __str__(self):
    return f'{self.user.username} (User ID: {self.user.id})'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to="profile_photo/", blank=True, null=True)

def __str__(self):
     return f"{self.user.username} (User ID: {self.user.id})"

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')  # Prevent duplicate follows

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"



