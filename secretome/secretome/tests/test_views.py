from django.test import TestCase
from django.contrib.auth.models import User

# Create your tests here.

class ViewTests(TestCase):

    def test_usageView(self):
        resp = self.client.get('/secmaps/usage', follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Purpose:', resp.content)
        self.assertIn(b'Main Tabs:', resp.content)
        self.assertIn(b'Databases:', resp.content)
        
    def test_databaseView(self):
        resp = self.client.get('/secmaps/databases', follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Secretome Databases', resp.content)
        self.assertIn(b'Database</TH><TH>count', resp.content)
        
