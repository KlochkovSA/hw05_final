from django.test import TestCase


class TestTemplatesURL(TestCase):
    def test_404_custom_template(self):
        template = 'core/404.html'
        response = self.client.get('/nonexistent_url/')
        self.assertTemplateUsed(response, template)
