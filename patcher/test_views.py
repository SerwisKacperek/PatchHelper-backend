from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

from django.contrib.auth.models import User
from patcher.models import Patch
from patcher.serializers import PatchSerializer

class PatchViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username='testuser', password='12345')
        
        self.patch1 = Patch.objects.create(
            title='Test Patch 1',
            version='1.0.0',
            description='This is a test patch',   
            user=self.user,
            state='published')
        self.patch2 = Patch.objects.create(
            title='Test Patch 2',
            version='1.0.0',
            description='This is a test patch',   
            user=self.user,
            state='draft')
        
        self.patch2.upvote(self.user)

    def test_list_patches(self):
        response = self.client.get(reverse('patch-list'), {'ordering': 'created'}) # serializer reverses the order by creation date
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

        patches = Patch.objects.all()
        serializer = PatchSerializer(patches, many=True)

        self.assertEqual(response.data["results"], serializer.data)

    def test_pagination(self):
        response = self.client.get(reverse('patch-list'), {'page': 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)
        

    def test_ordering(self):
        response = self.client.get(reverse('patch-list'), {'ordering': '-upvotes'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["title"], 'Test Patch 2')
        self.assertEqual(response.data["results"][1]["title"], 'Test Patch 1')

class UserPatchViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username='testuser', password='12345')
        
        self.patch1 = Patch.objects.create(
            title='Test Patch 1',
            version='1.0.0',
            description='This is a test patch',   
            user=self.user,
            state='published')
        self.patch2 = Patch.objects.create(
            title='Test Patch 2',
            version='1.0.0',
            description='This is a test patch',   
            user=self.user,
            state='draft')
        
        self.patch2.upvote(self.user)

    def test_list_user_patches(self):
        response = self.client.get(reverse('user-patches'), {'user_id': self.user.id, "ordering": "created"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

        patches = Patch.objects.filter(user=self.user)
        serializer = PatchSerializer(patches, many=True)

        self.assertEqual(response.data["results"], serializer.data)

    def test_list_user_patches_unauthenticated(self):
        response = self.client.get(reverse('user-patches'))

        self.assertEqual(response.status_code, 403)

    def test_list_user_patches_other_user(self):
        other_user = User.objects.create_user(username='otheruser', password='12345')
        response = self.client.get(reverse('user-patches'), {'user_id': other_user.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)

    def test_pagination(self):
        response = self.client.get(reverse('user-patches'), {'user_id': self.user.id, 'page': 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_ordering(self):
        response = self.client.get(reverse('user-patches'), {'user_id': self.user.id, 'ordering': '-upvotes'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["title"], 'Test Patch 2')
        self.assertEqual(response.data["results"][1]["title"], 'Test Patch 1')

class PatchCreateTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_create_patch(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(reverse('new-patch'), {
            'title': 'Test Patch',
            'version': '1.0.0',
            'description': 'This is a test patch',
            'state': 'published',
            'content': '[]'
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Patch.objects.count(), 1)

        patch = Patch.objects.first()

        self.assertEqual(patch.title, 'Test Patch')
        self.assertEqual(patch.version, '1.0.0')
        self.assertEqual(patch.description, 'This is a test patch')
        self.assertEqual(patch.state, 'published')
        self.assertEqual(patch.user, self.user)

    def test_create_patch_unauthenticated(self):
        response = self.client.post(reverse('new-patch'), {
            'title': 'Test Patch',
            'version': '1.0.0',
            'description': 'This is a test patch',
            'state': 'published',
            'content': '[]'
        })

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Patch.objects.count(), 0)

    def test_create_patch_missing_fields(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(reverse('new-patch'), {
            'title': 'Test Patch',
            'description': 'This is a test patch',
            'state': 'published',
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Patch.objects.count(), 0)

    def test_create_patch_invalid_state(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(reverse('new-patch'), {
            'title': 'Test Patch',
            'version': '1.0.0',
            'description': 'This is a test patch',
            'state': 'invalid'
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Patch.objects.count(), 0)
    
    def test_create_patch_invalid_content(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(reverse('new-patch'), {
            'title': 'Test Patch',
            'version': '1.0.0',
            'description': 'This is a test patch',
            'state': 'published',
            'content': 'invalid value - not a proper JSON array'
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Patch.objects.count(), 0)

class PatchContentViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username='testuser', password='12345')

        self.patch = Patch.objects.create(
            title='Test Patch',
            version='1.0.0',
            description='This is a test patch',   
            user=self.user,
            state='published')

    def test_list_patch_content(self):
        response = self.client.get(reverse('patch-content', kwargs={'uuid': self.patch.uuid}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_list_patch_content_not_found(self):
        response = self.client.get(reverse('patch-content', kwargs={'uuid': 'invalid-uuid'}))

        self.assertEqual(response.status_code, 404)

    def test_list_patch_content_unauthenticated(self):
        response = self.client.get(reverse('patch-content', kwargs={'uuid': self.patch.uuid}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

class UserViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        response = self.client.post(reverse('user-create'), {
            'username': 'testuser',
            'email': 'testuser@testmail.com',
            'password': '12345',
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)

    def test_create_user_already_authenticated(self):
        user = User.objects.create_user(username='testuser', password='12345')

        self.client.force_authenticate(user=user)

        response = self.client.post(reverse('user-create'), {
            'username': 'testuser',
            'email': 'testuser@testmail.com',
            'password': '12345',
        })

        self.assertEqual(response.status_code, 403)
        self.assertEqual(User.objects.count(), 1)

    def test_create_user_missing_fields(self):
        response = self.client.post(reverse('user-create'), {
            'username': 'testuser',
            'password': '12345',
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)
    
    def test_create_user_invalid_email(self):
        response = self.client.post(reverse('user-create'), {
            'username': 'testuser',
            'email': 'invalidemail',
            'password': '12345',
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)
    
    def test_create_user_short_values(self):
        response = self.client.post(reverse('user-create'), {
            'username': 'a',
            'email': 'foo@bar.com',
            'password': '12345',
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.post(reverse('user-create'), {
            'username': 'abcdef',
            'email': 'foo@bar.com',
            'password': '1',
        })
        self.assertEqual(response.status_code, 400)

        self.assertEqual(User.objects.count(), 0)

    def test_create_user_long_values(self):
        response = self.client.post(reverse('user-create'), {
            'username': 'a'*31,
            'email': 'foo@bar.com',
            'password': '12345',
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.post(reverse('user-create'), {
            'username': 'abcdef',
            'email': 'foo@bar.com',
            'password': '1'*129,
        })
        self.assertEqual(response.status_code, 400)

        self.assertEqual(User.objects.count(), 0)

    def test_create_user_valid_values(self):
        response = self.client.post(reverse('user-create'), {
            'username': 'testuser',
            'email': 'foo@bar.com',
            'password': '12345',
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
    
    def test_get_user_anon(self):
        user = User.objects.create_user(username='testuser', password='12345')

        response = self.client.get(reverse('user-detail'), {'user_id': user.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_get_user_self_authenticated(self):
        user = User.objects.create_user(username='testuser', password='12345')

        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('user-detail'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_get_user_self_unauthenticated(self):
        response = self.client.get(reverse('user-detail'))

        self.assertEqual(response.status_code, 403)

class ProfileDetailTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_profile_anon(self):
        response = self.client.get(reverse('current-profile'))

        self.assertEqual(response.status_code, 401)

    def test_get_profile_authenticated(self):
        user = User.objects.create_user(username='testuser', password='12345')

        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('current-profile'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_profile_authenticated_no_profile(self):
        user = User.objects.create_user(username='testuser', password='12345')

        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('current-profile'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_profile_authenticated_profile(self):
        user = User.objects.create_user(username='testuser', password='12345')
        profile = user.profile
        profile.bio = 'This is a test bio'
        profile.save()

        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('current-profile'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['bio'], 'This is a test bio')

class UpvotePostTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username='testuser', password='12345')

        self.patch = Patch.objects.create(
            title='Test Patch',
            version='1.0.0',
            description='This is a test patch',   
            user=self.user,
            state='published')

    def test_upvote_patch(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('upvote-patch', kwargs={'uuid': self.patch.uuid}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.patch.upvotes, 1)
        self.assertEqual(self.patch.upvoted_by.count(), 1)

    def test_upvote_patch_unauthenticated(self):
        response = self.client.post(reverse('upvote-patch', kwargs={'uuid': self.patch.uuid}))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.patch.upvotes, 0)
        self.assertEqual(self.patch.upvoted_by.count(), 0)

    def test_upvote_patch_already_upvoted(self):
        self.client.force_authenticate(user=self.user)

        self.patch.upvote(self.user)

        response = self.client.post(reverse('upvote-patch', kwargs={'uuid': self.patch.uuid}))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.patch.upvotes, 1)
        self.assertEqual(self.patch.upvoted_by.count(), 1)

    def test_upvote_patch_not_found(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('upvote-patch', kwargs={'uuid': 'invalid-uuid'}))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.patch.upvotes, 0)