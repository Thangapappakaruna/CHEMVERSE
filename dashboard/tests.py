"""CHEMVERSE end-to-end smoke tests.  Run with:  python manage.py test"""
import json

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from accounts.utils import make_verification_token
from chemistry_games.models import GameScore
from compound_search.models import Compound, FavoriteCompound
from molecular_structure.models import Structure
from reaction_builder.models import Reaction

User = get_user_model()


class SeededTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_data', verbosity=0)

    def login_demo(self):
        self.assertTrue(self.client.login(username='demo', password='ChemDemo@2026'))


class SeedTests(SeededTestCase):
    def test_counts(self):
        from chemistry_dictionary.models import Term
        from periodic_table.models import Element
        self.assertEqual(Element.objects.count(), 118)
        self.assertGreaterEqual(Compound.objects.count(), 50)
        self.assertGreaterEqual(Term.objects.count(), 60)
        self.assertTrue(Reaction.objects.filter(is_sample=True, is_balanced=True).exists())

    def test_seed_is_idempotent(self):
        call_command('seed_data', verbosity=0)
        self.assertEqual(User.objects.filter(username='demo').count(), 1)


class PublicPagesTests(SeededTestCase):
    def test_public_pages_ok(self):
        c = Compound.objects.first()
        r = Reaction.objects.filter(is_sample=True).first()
        urls = [
            '/', '/about/', '/contact/', '/accounts/login/', '/accounts/register/', '/accounts/password/reset/',
            '/learn/', '/learn/atoms/', '/periodic-table/', '/periodic-table/Fe/', '/compounds/', '/compounds/?q=ethanol',
            f'/compounds/{c.pk}/', '/boiling-melting/', '/boiling-melting/?t=50&elements=1', f'/boiling-melting/compare/?c={c.pk}',
            '/structure-lab/', '/structure-lab/gallery/', '/reactions/', f'/reactions/{r.pk}/', '/balancer/',
            '/balancer/?equation=Fe+%2B+O2+->+Fe2O3', '/games/', '/games/memory/', '/quiz/', '/quiz/leaderboard/',
            '/quiz/leaderboard/?board=games', '/quiz/leaderboard/?board=xp', '/molecular-weight/?formula=CuSO4%C2%B75H2O&grams=10',
            '/lab/', '/lab/titration/', '/lab/flame-test/', '/lab/ph-indicator/', '/lab/gas-laws/', '/lab/heating-curve/',
            '/dictionary/', '/dictionary/?letter=A', '/dictionary/acid/', '/community/', '/accounts/u/demo/',
        ]
        for slug in ('guess-element', 'periodic-challenge', 'formula-match', 'weight-challenge', 'boiling-challenge', 'timed-quiz'):
            urls.append(f'/games/{slug}/')
        for u in urls:
            with self.subTest(url=u):
                self.assertEqual(self.client.get(u).status_code, 200, u)

    def test_login_required_redirects(self):
        for u in ('/accounts/saved/', '/community/new/', '/compounds/add/', '/reactions/1/edit/'):
            with self.subTest(url=u):
                self.assertEqual(self.client.get(u).status_code, 302)

    def test_404(self):
        self.assertEqual(self.client.get('/periodic-table/Xx/').status_code, 404)

    def test_json_apis(self):
        self.assertEqual(len(self.client.get('/periodic-table/api/elements/').json()['elements']), 118)
        self.assertGreater(self.client.get('/compounds/api/search/?q=acid').json()['count'], 0)
        d = self.client.get('/balancer/api/', {'equation': 'C3H8 + O2 -> CO2 + H2O'}).json()
        self.assertEqual(d['coefficients'], [1, 5, 3, 4])
        self.assertAlmostEqual(self.client.get('/molecular-weight/api/', {'formula': 'H2O'}).json()['molar_mass'], 18.015, 2)
        self.assertTrue(self.client.get('/reactions/api/check/', {'reactants': '2H2 + O2', 'products': '2H2O'}).json()['is_balanced'])
        self.assertEqual(len(self.client.get('/quiz/api/questions/?n=5').json()['questions']), 5)


class GuestModeTests(SeededTestCase):
    """Every tool must work without signing in."""

    def test_guest_dashboard_and_tools(self):
        for u in ('/dashboard/', '/quiz/play/?n=5', '/reactions/new/'):
            with self.subTest(url=u):
                self.assertEqual(self.client.get(u).status_code, 200, u)
        self.assertContains(self.client.get('/dashboard/'), 'Guest dashboard')

    def test_guest_quiz_kept_in_session(self):
        self.client.get('/quiz/play/?n=5')
        ids = self.client.session['quiz_ids']
        self.assertContains(self.client.post('/quiz/play/', {f'q{i}': 'a' for i in ids}), 'Your score')
        self.assertEqual(len(self.client.session['guest']['quiz']), 1)

    def test_guest_game_lesson_lab(self):
        d = self.client.post('/games/api/submit/', json.dumps({'game': 'memory', 'points': 300}), content_type='application/json').json()
        self.assertTrue(d['ok'] and d['guest'])
        self.assertFalse(GameScore.objects.filter(points=300).exists())
        self.client.post('/learn/atoms/complete/')
        self.assertIn('atoms', self.client.session['guest']['lessons'])
        d = self.client.post('/lab/titration/record/', json.dumps({'result': 'pH 7'}), content_type='application/json').json()
        self.assertTrue(d['guest'])
        self.assertContains(self.client.get('/dashboard/'), '300')

    def test_guest_reaction_check(self):
        res = self.client.post('/reactions/new/', {'title': 'Water', 'reactants': 'H2 + O2', 'products': 'H2O', 'reaction_type': 'auto'})
        self.assertContains(res, 'Balancing help')
        self.assertFalse(Reaction.objects.filter(title='Water').exists())


class AuthTests(SeededTestCase):
    def test_register_verify_login_logout(self):
        res = self.client.post('/accounts/register/', {'username': 'new_chemist', 'email': 'NEW@example.com', 'full_name': 'New',
                                                       'password1': 'Benzene#Ring42', 'password2': 'Benzene#Ring42'})
        self.assertRedirects(res, '/dashboard/')
        user = User.objects.get(username='new_chemist')
        self.assertEqual(user.email, 'new@example.com')
        self.assertFalse(user.profile.email_verified)
        self.assertEqual(len(mail.outbox), 1)
        self.client.get(reverse('accounts:verify_email', args=[make_verification_token(user)]))
        user.profile.refresh_from_db()
        self.assertTrue(user.profile.email_verified)
        self.client.post('/accounts/logout/')
        self.assertTrue(self.client.login(username='new@example.com', password='Benzene#Ring42'))  # email login

    def test_duplicate_user_id_rejected(self):
        res = self.client.post('/accounts/register/', {'username': 'DEMO', 'email': 'x@example.com',
                                                       'password1': 'Benzene#Ring42', 'password2': 'Benzene#Ring42'})
        self.assertContains(res, 'already taken')

    def test_login_view_with_email(self):
        res = self.client.post('/accounts/login/', {'username': 'demo@chemverse.local', 'password': 'ChemDemo@2026'})
        self.assertRedirects(res, '/dashboard/')

    def test_password_reset_email(self):
        self.client.post('/accounts/password/reset/', {'email': 'demo@chemverse.local'})
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/accounts/password/reset/', mail.outbox[0].body)


class UserFeatureTests(SeededTestCase):
    def setUp(self):
        self.login_demo()

    def test_private_pages(self):
        for u in ('/dashboard/', '/accounts/profile/edit/', '/accounts/history/', '/accounts/saved/', '/reactions/new/',
                  '/community/new/', '/compounds/add/', '/accounts/password/change/'):
            with self.subTest(url=u):
                self.assertEqual(self.client.get(u).status_code, 200, u)

    def test_favorite_toggle(self):
        c = Compound.objects.get(name='Benzene')
        self.client.post(f'/compounds/{c.pk}/favorite/', HTTP_ACCEPT='application/json')
        self.assertTrue(FavoriteCompound.objects.filter(user__username='demo', compound=c).exists())

    def test_save_structure(self):
        payload = {'name': 'Methane', 'atoms': [{'el': 'C', 'x': 100, 'y': 100}] + [{'el': 'H', 'x': 100 + i, 'y': 50} for i in range(4)],
                   'bonds': [{'a': 0, 'b': i, 'order': 1} for i in range(1, 5)]}
        d = self.client.post('/structure-lab/save/', json.dumps(payload), content_type='application/json').json()
        self.assertTrue(d['ok'])
        self.assertEqual(Structure.objects.get(pk=d['id']).formula, 'CH4')

    def test_create_reaction_and_balance(self):
        res = self.client.post('/reactions/new/', {'title': 'Ammonia', 'reactants': 'N2 + H2', 'products': 'NH3', 'reaction_type': 'auto', 'is_public': 'on'})
        r = Reaction.objects.get(title='Ammonia')
        self.assertRedirects(res, f'/reactions/{r.pk}/')
        self.assertFalse(r.is_balanced)
        self.client.post(f'/reactions/{r.pk}/balance/')
        r.refresh_from_db()
        self.assertTrue(r.is_balanced)
        self.assertEqual(r.equation, 'N2 + 3H2 -> 2NH3')

    def test_game_submit_and_limits(self):
        ok = self.client.post('/games/api/submit/', json.dumps({'game': 'memory', 'points': 500}), content_type='application/json').json()
        self.assertTrue(ok['ok'])
        bad = self.client.post('/games/api/submit/', json.dumps({'game': 'memory', 'points': 999999}), content_type='application/json')
        self.assertEqual(bad.status_code, 400)
        self.assertTrue(GameScore.objects.filter(user__username='demo', points=500).exists())

    def test_quiz_flow(self):
        self.client.get('/quiz/play/?n=5')
        ids = self.client.session['quiz_ids']
        res = self.client.post('/quiz/play/', {f'q{i}': 'a' for i in ids})
        self.assertContains(res, 'Your score')

    def test_community_post_and_reply(self):
        res = self.client.post('/community/new/', {'title': 'Testing posts', 'category': 'question', 'body': 'Hello chemists'})
        self.assertEqual(res.status_code, 302)
        from community.models import Post
        p = Post.objects.get(title='Testing posts')
        self.client.post(f'/community/{p.pk}/', {'body': 'A reply'})
        self.assertEqual(p.comments.count(), 1)

    def test_lab_record(self):
        d = self.client.post('/lab/titration/record/', json.dumps({'result': 'pH 7 at 25 mL'}), content_type='application/json').json()
        self.assertTrue(d['ok'])

    def test_contact(self):
        res = self.client.post('/contact/', {'name': 'Demo', 'email': 'demo@chemverse.local', 'subject': 'Hi', 'message': 'Great site'})
        self.assertRedirects(res, '/contact/')
