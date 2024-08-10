from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User

class Patch(models.Model):
    title = models.CharField(max_length=50, blank=True, default='', unique=True)
    version = models.CharField(max_length=10, blank=True, default='')
    description = models.TextField(max_length=250, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    upvotes = models.IntegerField(default=0)
    upvoted_by = models.ManyToManyField(User, related_name='upvoted_patches', blank=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.user:
            raise ValueError('Creator must be set')
        if not self.upvotes:
            self.upvotes = 0
        
        super(Patch, self).save(*args, **kwargs)

    def upvote(self, user):
        if not self.upvoted_by.filter(id=user.id).exists():
            self.upvoted_by.add(user)
            self.upvotes += 1
            self.save()
            return True
        return False

class PatchContent(models.Model):
    post = models.ForeignKey(Patch, related_name='content', on_delete=models.CASCADE)
    type = models.TextField(max_length=15, blank=True, default='textField')
    text = models.TextField(max_length=500, blank=True, null=True, default='')
    images = ArrayField(models.ImageField(upload_to='images/'), blank=True, null=True, default=list)
    order = models.IntegerField()

class LandingPageStat(models.Model):
    value = models.IntegerField()
    description = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['description']

    def __str__(self):
        return self.description
    
    def __int__(self):
        return self.value
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='avatars/default.svg')
    bio = models.TextField(max_length=250, blank=True)
    joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
    def get_default_bio(self):
        return f"We don't know much about them, but we're sure {self.user.username} is great."
    
    def save(self, *args, **kwargs):
        if not self.bio:
            self.bio = self.get_default_bio()
        super(Profile, self).save(*args, **kwargs)