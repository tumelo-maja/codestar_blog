from django.test import TestCase
from .forms import CollaborateForm


class TestCollaborateForm(TestCase):

    def test_form_is_valid(self):
        """ Test for all fields"""
        form = CollaborateForm({
            'name': 'TM',
            'email': 'test@test.com',
            'message': 'Hello!'
        })
        self.assertTrue(form.is_valid(), msg="Form is not valid")

    def test_name_is_required(self):
        """Test for the 'name' field"""
        form = CollaborateForm({
            'name': '',
            'email': 'name@name.com',
            'message': 'Its the name!'
        })
        self.assertTrue(form.is_valid(),
                        msg="name was not provided, but the form is valid")

    def test_email_is_valid(self):
        """Test for the 'email' field"""
        form = CollaborateForm({
            'name': 'john',
            'email': '',
            'message': 'Its the email!'
        })
        self.assertTrue(form.is_valid(),
                        msg="email was not provided, but the form is valid")

    def test_message_is_valid(self):
        """Test for the 'message' field"""
        form = CollaborateForm({
            'name': 'john',
            'email': 'message@message.com',
            'message': ''
        })
        self.assertTrue(form.is_valid(),
                        msg="message was not provided, but the form is valid")
