from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class SignupTests(TestCase):
    def test_signup_url_accessible(self):
        """Verify the signup page loads successfully."""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

    def test_signup_redirect_if_logged_in(self):
        """Verify logged-in users are redirected to homepage when visiting signup page."""
        user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('signup'))
        self.assertRedirects(response, '/')

    def test_signup_form_submission_success(self):
        """Verify that submitting valid signup data creates a user and logs them in."""
        signup_data = {
            'username': 'newuser',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = self.client.post(reverse('signup'), data=signup_data)
        
        # Should redirect to home page upon successful registration
        self.assertRedirects(response, '/')
        
        # Verify user was created in the database
        user_exists = User.objects.filter(username='newuser').exists()
        self.assertTrue(user_exists)
        
        # Verify the new user is authenticated
        user = User.objects.get(username='newuser')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
