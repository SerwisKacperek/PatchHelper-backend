from django.db import models
from jsonfield import JSONField

class Post(models.Model):
    title = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    content = JSONField()

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.title

class LandingPageStat(models.Model):
    value = models.IntegerField()
    description = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['description']

    def __str__(self):
        return self.description
    
    def __int__(self):
        return self.value

class TextFieldComponent(models.Model):
    post = models.ForeignKey(Post, related_name='textfield', on_delete=models.CASCADE)
    text = models.TextField()

class ImageComponent(models.Model):
    post = models.ForeignKey(Post, related_name='imagefield', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    image_description = models.CharField(max_length=100, blank=True, default='')
    alt_text = models.CharField(max_length=50, blank=True, default='')