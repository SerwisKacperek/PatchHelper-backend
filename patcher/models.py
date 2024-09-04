import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User

class Patch(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=50, blank=True, default='', unique=False)
    thumbnail = models.ImageField(upload_to="thumbnails/", null=True, blank=True)
    version = models.CharField(max_length=10, blank=True, default='1.0.0')
    description = models.TextField(max_length=250, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    upvotes = models.IntegerField(default=0)
    upvoted_by = models.ManyToManyField(User, related_name='upvoted_patches', blank=True)

    STATE_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('hidden', 'Hidden')
    ]

    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='draft')

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
    post = models.ForeignKey(Patch, null=True, blank=True, related_name='content', on_delete=models.CASCADE)
    text = models.TextField(max_length=500, blank=True, null=True, default='')
    images = ArrayField(models.ImageField(upload_to='images/'), blank=True, null=True, default=list)
    order = models.IntegerField()

    TYPE_CHOICES = [
        ('textField', 'Text Field'),
        ('singleImage', 'Single Image'),
        ('imageGallery', 'Image Gallery'),
    ]

    type = models.TextField(max_length=15, choices=TYPE_CHOICES, blank=False, default='textField')

    def save(self, *args, **kwargs):

        if not self.order:
            self.order = 1
        if not self.post:
            raise ValueError("Post must be set")
        if self.type == 'singleImage' and len(self.images) > 1:
            raise ValueError("Single Image content type can only have one image")
        if self.type == 'singleImage' or self.type == 'imageGallery' and len(self.images) == 0:
            raise ValueError("Image content type must have at least one image")
        if self.type == 'textField' and len(self.images) > 0:
            raise ValueError("Text content type cannot have images")
        
        super(PatchContent, self).save(*args, **kwargs)

class LandingPageStat(models.Model):
    value = models.IntegerField()
    description = models.CharField(max_length=100)

    class Meta:
        ordering = ['description']

    def save(self, *args, **kwargs):
        if not self.description:
            raise ValueError('Description must be set')
        if not self.value:
            raise ValueError('Value must be set')
        
        super(LandingPageStat, self).save(*args, **kwargs)

    def __str__(self):
        return self.description
    
    def __int__(self):
        return self.value
    
class Profile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='avatars/default.svg')
    bio = models.TextField(max_length=250, blank=True)
    joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
    def get_default_bio(self):
        return f"We don't know much about them, but we're sure {self.user.username} is great."
    
    def save(self, *args, **kwargs):
        if not self.user:
            raise ValueError('User must be set')
        if not self.bio:
            self.bio = self.get_default_bio()
            
        super(Profile, self).save(*args, **kwargs)