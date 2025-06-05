from django.test import TestCase
from django.urls import reverse
from .models import About
from .forms import CollaborateForm


class TestAboutViews(TestCase):

    def setUp(self):
        """Creates about me content"""
        self.about = About(title="All about me",
                         content="Completed the django content")
        self.about.save()    

    def test_render_about_me_page_with_collaborate_form(self):
        """Verifies get request for about me containing a collaboration form"""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"All about me", response.content)
        self.assertIn(b"Completed the django content", response.content)
        self.assertIsInstance(
            response.context['collaborate_form'], CollaborateForm)
        self.assertIsInstance(
            response.context['about'], About)        