from django.test import TestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from django.contrib.auth import models as auth_models
from patcher.models import Patch, PatchContent
from patcher.serializers import PatchSerializer

import os
import time

class TestPatchViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = auth_models.User.objects.create_user(username='testuser', password='12345')
        
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
            state='published')
        self.patch3 = Patch.objects.create(
            title='Test Patch 3',
            version='1.0.0',
            description='This is a draft test patch',
            user=self.user,
            state='draft'
        )
        self.patch4 = Patch.objects.create(
            title='Test Patch 4',
            version='1.0.0',
            description='This is a hidden test patch',
            user=self.user,
            state='hidden'
        )
        
        self.patch2.upvote(self.user)

    def test_list_patches(self):
        response = self.client.get(reverse('patch-list'), {'ordering': '-created'}) # serializer reverses the order by creation date

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

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

class TestUserPatchViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = auth_models.User.objects.create_user(username='testuser', password='12345')
        
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
        other_user = auth_models.User.objects.create_user(username='otheruser', password='12345')
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

class TestPatchCreate(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = auth_models.User.objects.create_user(username='testuser', password='12345')

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

    def test_create_patch_content(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(reverse('new-patch'), {
            'title': 'Test Patch',
            'version': '1.0.0',
            'description': 'This is a test patch',
            'state': 'published',
            'content': '[{"text": "This is a test content", "order": 1, "type": "textField"}]'
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Patch.objects.count(), 1)

        patch = Patch.objects.first()

        self.assertEqual(patch.title, 'Test Patch')
        self.assertEqual(patch.version, '1.0.0')
        self.assertEqual(patch.description, 'This is a test patch')
        self.assertEqual(patch.state, 'published')
        self.assertEqual(patch.user, self.user)

        self.assertEqual(patch.content.count(), 1)
        self.assertEqual(patch.content.first().text, 'This is a test content')
        self.assertEqual(patch.content.first().order, 1)
        self.assertEqual(patch.content.first().type, 'textField')

        # invalid content
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('new-patch'), {
            'title': 'Test Patch',
            'version': '1.0.0',
            'description': 'This is a test patch',
            'state': 'published',
            'content': '[{"text": "abc", "order": 1, "type": "invalid-type"}]'
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Patch.objects.count(), 1)

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

class TestPatchContentViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = auth_models.User.objects.create_user(username='testuser', password='12345')

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

class TestUserViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        response = self.client.post(reverse('user-create'), {
            'username': 'testuser',
            'email': 'testuser@testmail.com',
            'password': '12345',
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(auth_models.User.objects.count(), 1)

    def test_create_user_already_authenticated(self):
        user = auth_models.User.objects.create_user(username='testuser', password='12345')

        self.client.force_authenticate(user=user)

        response = self.client.post(reverse('user-create'), {
            'username': 'testuser',
            'email': 'testuser@testmail.com',
            'password': '12345',
        })

        self.assertEqual(response.status_code, 403)
        self.assertEqual(auth_models.User.objects.count(), 1)

    def test_create_user_missing_fields(self):
        response = self.client.post(reverse('user-create'), {
            'username': 'testuser',
            'password': '12345',
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(auth_models.User.objects.count(), 0)

    def test_create_user_invalid_email(self):
        response = self.client.post(reverse('user-create'), {
            'username': 'testuser',
            'email': 'invalidemail',
            'password': '12345',
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(auth_models.User.objects.count(), 0)

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

        self.assertEqual(auth_models.User.objects.count(), 0)

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

        self.assertEqual(auth_models.User.objects.count(), 0)

    def test_create_user_valid_values(self):
        response = self.client.post(reverse('user-create'), {
            'username': 'testuser',
            'email': 'foo@bar.com',
            'password': '12345',
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(auth_models.User.objects.count(), 1)

    def test_get_user_anon(self):
        user = auth_models.User.objects.create_user(username='testuser', password='12345')

        response = self.client.get(reverse('user-detail'), {'user_id': user.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_user_self_authenticated(self):
        user = auth_models.User.objects.create_user(username='testuser', password='12345')

        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('user-detail'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_user_self_unauthenticated(self):
        response = self.client.get(reverse('user-detail'))

        self.assertEqual(response.status_code, 403)

class TestProfileDetail(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_profile_anon(self):
        response = self.client.get(reverse('current-profile'))

        self.assertEqual(response.status_code, 401)

    def test_get_profile_authenticated(self):
        user = auth_models.User.objects.create_user(username='testuser', password='12345')

        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('current-profile'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_profile_authenticated_no_profile(self):
        user = auth_models.User.objects.create_user(username='testuser', password='12345')

        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('current-profile'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_profile_authenticated_profile(self):
        user = auth_models.User.objects.create_user(username='testuser', password='12345')
        profile = user.profile
        profile.bio = 'This is a test bio'
        profile.save()

        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('current-profile'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['bio'], 'This is a test bio')

class TestUpvotePost(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = auth_models.User.objects.create_user(username='testuser', password='12345')

        self.patch = Patch.objects.create(
            title='Test Patch',
            version='1.0.0',
            description='This is a test patch',   
            user=self.user,
            state='published')

    def test_upvote_patch(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('upvote-patch', kwargs={'uuid': self.patch.uuid}))

        self.patch.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.patch.upvoted_by.count(), 1)
        self.assertEqual(self.patch.upvotes, 1)

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

class TestPatchUpdate(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = auth_models.User.objects.create_user(username='testuser', password='12345')

        self.patch = Patch.objects.create(
            title='Test Patch',
            version='1.0.0',
            description='This is a test patch',   
            user=self.user,
            state='published')

        self.advanced_patch = Patch.objects.create(
            title='Advanced Patch',
            version='1.0.0',
            description='This is an advanced test patch',   
            user=self.user,
            state='published',
        )
        self.patch_content1 = PatchContent.objects.create(
            post=self.advanced_patch,
            text='This is a test content',
            order=0,
            type='textField'
        )
    
    def test_update_patch(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(reverse('update-patch', kwargs={'uuid': self.patch.uuid}), {
            'title': 'Updated Patch',
            'version': '1.0.1',
            'description': 'This is an updated test patch',
            'state': 'draft'
        })

        self.assertEqual(response.status_code, 200)

        self.patch.refresh_from_db()

        self.assertEqual(self.patch.title, 'Updated Patch')
        self.assertEqual(self.patch.version, '1.0.1')
        self.assertEqual(self.patch.description, 'This is an updated test patch')
        self.assertEqual(self.patch.state, 'draft')
    
    def test_update_patch_unauthenticated(self):
        response = self.client.patch(reverse('update-patch', kwargs={'uuid': self.patch.uuid}), {
            'title': 'Updated Patch',
            'version': '1.0.1',
            'description': 'This is an updated test patch',
            'state': 'draft'
        })

        self.assertEqual(response.status_code, 403)

        self.patch.refresh_from_db()

        self.assertEqual(self.patch.title, 'Test Patch')
        self.assertEqual(self.patch.version, '1.0.0')
        self.assertEqual(self.patch.description, 'This is a test patch')
        self.assertEqual(self.patch.state, 'published')
    
    def test_update_patch_invalid_uuid(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(reverse('update-patch', kwargs={'uuid': "invalid-uuid"}), {
            'title': 'Updated Patch',
            'version': '1.0.1',
            'description': 'This is an updated test patch',
            'state': 'draft'
        })

        self.assertEqual(response.status_code, 404)

        self.patch.refresh_from_db()

        self.assertEqual(self.patch.title, 'Test Patch')
        self.assertEqual(self.patch.version, '1.0.0')
        self.assertEqual(self.patch.description, 'This is a test patch')
        self.assertEqual(self.patch.state, 'published')

    def test_update_patch_content(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(reverse('update-patch', kwargs={'uuid': self.advanced_patch.uuid}), {
            'title': 'Updated Patch',
            'version': '1.0.1',
            'description': 'This is an updated test patch',
            'state': 'draft',
            'content': '[{"id": '+ str(self.patch_content1.id) + ', "text": "Updated content", "order": 0, "type": "textField"}]'
        })

        self.assertEqual(response.status_code, 200)

        self.advanced_patch.refresh_from_db()
        self.patch_content1.refresh_from_db()

        self.assertEqual(self.advanced_patch.title, 'Updated Patch')
        self.assertEqual(self.advanced_patch.version, '1.0.1')
        self.assertEqual(self.advanced_patch.description, 'This is an updated test patch')
        self.assertEqual(self.advanced_patch.state, 'draft')

        self.assertEqual(self.patch_content1.text, 'Updated content')
    
    def test_update_patch_content_invalid(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(reverse('update-patch', kwargs={'uuid': self.advanced_patch.uuid}), {
            'title': 'Updated Patch',
            'version': '1.0.1',
            'description': 'This is an updated test patch',
            'state': 'draft',
            'content': 'invalid content'
        })

        self.assertEqual(response.status_code, 400)

        self.advanced_patch.refresh_from_db()
        self.patch_content1.refresh_from_db()

        self.assertEqual(self.advanced_patch.title, 'Updated Patch')
        self.assertEqual(self.advanced_patch.version, '1.0.1')
        self.assertEqual(self.advanced_patch.description, 'This is an updated test patch')
        self.assertEqual(self.advanced_patch.state, 'draft')
    
    def test_update_patch_content_invalid_id(self):
        self.client.force_authenticate(user=self.user)

        # invalid id
        response = self.client.patch(reverse('update-patch', kwargs={'uuid': self.patch.uuid}), {
            'title': 'Updated Patch',
            'version': '1.0.1',
            'description': 'This is an updated test patch',
            'state': 'draft',
            'content': '[{"id": "999", "text": "Updated content", "order": 0, "type": "textField"}]'
        })

        self.assertEqual(response.status_code, 400)

        self.patch.refresh_from_db()

        self.assertEqual(self.patch.title, 'Updated Patch')
        self.assertEqual(self.patch.version, '1.0.1')
        self.assertEqual(self.patch.description, 'This is an updated test patch')
        self.assertEqual(self.patch.state, 'draft')

        # no id provided
        response = self.client.patch(reverse('update-patch', kwargs={'uuid': self.patch.uuid}), {
            'title': 'Updated Patch',
            'version': '1.0.1',
            'description': 'This is an updated test patch',
            'state': 'draft',
            'content': '[{"text": "Updated content", "order": 0, "type": "textField"}]'
        })

        self.assertEqual(response.status_code, 400)
        self.patch.refresh_from_db()

class TestUploadView(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = auth_models.User.objects.create_user(username='testuser', password='12345')
        self.image_path = os.path.join(os.path.dirname(__file__), 'test_image.png')

        with open(self.image_path, 'wb') as img:
            img.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xff\xa0\x00\x00\x00\nIDAT\x08\xd7c\xf8\x0f\x00\x01\x05\x01\x01\x00\x00\x00\x00IEND\xaeB`\x82')

    def tearDown(self):

        # ensure the file is closed before trying to delete it
        time.sleep(1)

        if os.path.exists(self.image_path):
            os.remove(self.image_path)

    def test_upload_image(self):
        self.client.force_authenticate(user=self.user)

        with open(self.image_path, 'rb') as img:
            # Create a SimpleUploadedFile object to simulate file upload
            uploaded_file = SimpleUploadedFile(name='test_image.png', content=img.read(), content_type='image/png')

            # Make the POST request with the file
            response = self.client.post(reverse('upload'), {'file': uploaded_file}, format='multipart')

            # Assert the upload was successful
            self.assertEqual(response.status_code, 201)
            self.assertIn('url', response.data)  # Check if 'location' is in the response
            self.assertTrue(response.data['url'].endswith('.png'))

    def test_upload_image_unauthenticated(self):
        with open(self.image_path, 'rb') as img:
            # Create a SimpleUploadedFile object to simulate file upload
            uploaded_file = SimpleUploadedFile(name='test_image.png', content=img.read(), content_type='image/png')

            # Make the POST request with the file
            response = self.client.post(reverse('upload'), {'file': uploaded_file}, format='multipart')

            # Assert the upload was successful
            self.assertEqual(response.status_code, 401)
    
    def test_upload_image_invalid(self):
        self.client.force_authenticate(user=self.user)

        # Make the POST request with the file
        response = self.client.post(reverse('upload'), {'file': 'invalid file'}, format='multipart')

        # Assert the upload was successful
        self.assertEqual(response.status_code, 400)