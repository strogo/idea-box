from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from idea import models
from idea.tests.utils import random_user

class VotingTests(TestCase):
    fixtures = ['state']

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@agency.gov', 'password')
        self.state = models.State.objects.get(name='Active') 

    def test_good_vote(self):
        user = random_user()
        idea = models.Idea(creator=user, title='Transit subsidy to Mars', 
                    text='Aliens need assistance.', state=self.state)
        idea.save()

        self.client.login(username='testuser', password='password')

        resp = self.client.post(reverse('upvote_idea'), {'idea_id':idea.id, 'next':reverse('idea_detail', args=(idea.id,))})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(idea.vote_set.all()), 1)

    def test_vote_twice(self):
        """
            Voting twice shouldn't do anything to the vote count (it's
            idempotent).
        """
        idea = models.Idea(creator=random_user(), title='Transit subsidy to Mars', 
                    text='Aliens need assistance.', state=self.state)
        idea.save()

        self.client.login(username='testuser', password='password')
        resp = self.client.post(reverse('upvote_idea'), {'idea_id':idea.id, 'next':reverse('idea_detail', args=(idea.id,))})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(idea.vote_set.all()), 1)

        resp = self.client.post(reverse('upvote_idea'), {'idea_id':idea.id, 'next':reverse('idea_detail', args=(idea.id,))})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(idea.vote_set.all()), 1)

    def test_must_logged_in(self):
        """ 
            A user must be logged in to vote. 
        """
        idea = models.Idea(creator=random_user(), title='Transit subsidy to Mars', 
                    text='Aliens need assistance.', state=self.state)
        idea.save()
        resp = self.client.post(reverse('upvote_idea'), {'idea_id':idea.id, 'next':reverse('idea_detail', args=(idea.id,))})
        self.assertIn('up', resp['Location'])

