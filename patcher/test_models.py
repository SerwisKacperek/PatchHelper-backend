from django.test import TestCase
from django.contrib.auth.models import User

from patcher.models import Patch, PatchContent, LandingPageStat, Profile

class PatchTestCase(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='patch_author', password='12345')
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='12345')
    
    def test_create_patch(self):
        patch = Patch.objects.create(
            title='Test Patch',
            version='1.0.0',
            description='This is a test patch',   
            user=self.author,
            state='published')
        
        self.assertEqual(str(patch), patch.title)
        self.assertEqual(patch.title, 'Test Patch')
        self.assertEqual(patch.version, '1.0.0')
        self.assertEqual(patch.description, 'This is a test patch')
        self.assertEqual(patch.user, self.author)
        self.assertEqual(patch.upvotes, 0)
        self.assertEqual(patch.state, 'published')
        
    def test_create_patch_default(self):
        patch = Patch.objects.create(
            title='Test Patch',
            description='This is a test patch',   
            user=self.author)
        
        self.assertEqual(patch.state, 'draft')
        self.assertEqual(patch.version, '1.0.0')
        self.assertEqual(patch.user, self.author)

    def test_create_patch_no_author(self):
        with self.assertRaises(ValueError):
            patch = Patch.objects.create(
                title='Test Patch',
                description='This is a test patch')

    def test_upvote(self):
        patch = Patch.objects.create(
            title='Test Patch',
            description='This is a test patch',   
            user=self.author)
        
        self.assertEqual(patch.upvotes, 0)
        self.assertEqual(patch.upvote(self.user1), True)
        self.assertEqual(patch.upvotes, 1)
        self.assertEqual(patch.upvote(self.user2), True)
        self.assertEqual(patch.upvotes, 2)
        self.assertEqual(patch.upvote(self.user1), False)
        self.assertEqual(patch.upvotes, 2)

class PatchContentTestCase(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='patch_author', password='12345')
        self.patch = Patch.objects.create(
            title='Test Patch',
            description='This is a test patch',   
            user=self.author)
    
    def test_create_patch_content(self):
        content = PatchContent.objects.create(
            post=self.patch,
            type='textField',
            text='This is a test content',
            order=1)
        
        self.assertEqual(content.post, self.patch)
        self.assertEqual(content.type, 'textField')
        self.assertEqual(content.text, 'This is a test content')
        self.assertEqual(content.order, 1)

    def test_create_patch_content_image(self):
        content = PatchContent.objects.create(
            post=self.patch,
            type='imageField',
            images=['image1.jpg', 'image2.jpg'],
            order=1)
        
        self.assertEqual(content.post, self.patch)
        self.assertEqual(content.type, 'imageField')
        self.assertEqual(content.images, ['image1.jpg', 'image2.jpg'])
        self.assertEqual(content.order, 1)

    def test_create_patch_content_no_post(self):
        with self.assertRaises(ValueError):
            content = PatchContent.objects.create(
                type='textField',
                text='This is a test content',
                order=1)

    def test_create_patch_content_no_type(self):
        content = PatchContent.objects.create(
            post=self.patch,
            text='This is a test content',
            order=1)
        
        self.assertEqual(content.type, 'textField')
        self.assertEqual(content.text, 'This is a test content')

    def test_create_patch_content_no_order(self):
        content = PatchContent.objects.create(
            post=self.patch,
            type='textField',
            text='This is a test content')
        
        self.assertEqual(content.order, 1)

    def test_create_patch_content_no_text(self):
        content = PatchContent.objects.create(
            post=self.patch,
            type='textField',
            order=1)
        
        self.assertEqual(content.text, '')

    def test_create_patch_content_no_images(self):
        with self.assertRaises(ValueError):
            content = PatchContent.objects.create(
                post=self.patch,
                type='singleImage',
                order=1)
        with self.assertRaises(ValueError):
            content = PatchContent.objects.create(
                post=self.patch,
                type='imageGallery',
                order=1)
    
    def test_create_patch_content_single_image(self):
        with self.assertRaises(ValueError):
            content = PatchContent.objects.create(
                post=self.patch,
                type='singleImage',
                images=['image1.jpg', 'image2.jpg'],
                order=1)
    
    def test_create_patch_content_text_images(self):
        with self.assertRaises(ValueError):
            content = PatchContent.objects.create(
                post=self.patch,
                type='textField',
                images=['image1.jpg', 'image2.jpg'],
                order=1)
            
class LandingPageStatTestCase(TestCase):
    def test_create_landing_page_stat(self):
        stat = LandingPageStat.objects.create(
            value=100,
            description='Test Stat')
        
        self.assertEqual(stat.value, 100)
        self.assertEqual(stat.description, 'Test Stat')
        self.assertEqual(str(stat), stat.description)
        self.assertEqual(int(stat), 100)
        self.assertEqual(LandingPageStat.objects.count(), 1)
        
    def test_create_landing_page_stat_no_value(self):
        with self.assertRaises(ValueError):
            stat = LandingPageStat.objects.create(
                description='Test Stat')
        
    def test_create_landing_page_stat_no_description(self):
        with self.assertRaises(ValueError):
            stat = LandingPageStat.objects.create(
                value=100)
        
    def test_landing_page_stat_ordering(self):
        stat1 = LandingPageStat.objects.create(
            value=100,
            description='Stat 1')
        stat2 = LandingPageStat.objects.create(
            value=200,
            description='Stat 2')
        stat3 = LandingPageStat.objects.create(
            value=300,
            description='Stat 3')
        
        stats = LandingPageStat.objects.all()
        self.assertEqual(stats[0], stat1)
        self.assertEqual(stats[1], stat2)
        self.assertEqual(stats[2], stat3)

class ProfileTestCase(TestCase):
    def test_create_profile_default(self):
        user = User.objects.create_user(username='profiletest_default', password='12345')
        profile = Profile.objects.get(user=user)
        profile.bio = 'This is a test bio'
        
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.bio, 'This is a test bio')
        self.assertEqual(str(profile), profile.user.username)
        self.assertEqual(profile.avatar, 'avatars/default.svg')
        self.assertEqual(Profile.objects.count(), 1)
    
    def test_create_profile_no_user(self):
        with self.assertRaises(ValueError):
            profile = Profile.objects.create(
                bio='This is a test bio')
    
    def test_create_profile_no_bio(self):
        user = User.objects.create_user(username='profiletest_no_bio', password='12345')
        profile = Profile.objects.get(user=user)
        
        self.assertEqual(profile.bio, f"We don't know much about them, but we're sure {user.username} is great.")
        self.assertEqual(profile.avatar, 'avatars/default.svg')