"""Load CHEMVERSE sample data (idempotent – safe to run again).

    python manage.py seed_data            # reference data + demo users
    python manage.py seed_data --no-demo  # reference data only
"""
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Profile
from chemistry_dictionary.models import Term
from chemistry_games.models import Game, GameScore
from chemistry_learning.models import Lesson, LessonProgress
from chemistry_quiz.models import Question, QuizResult
from community.models import Comment, Post
from compound_search.models import ChemicalProperty, Compound, FavoriteCompound, SearchHistory
from config.chem import composition, load_seed
from dashboard.models import Activity
from lab_simulator.models import Experiment, ExperimentLog
from molecular_structure.models import Structure
from periodic_table.models import Element
from reaction_builder.logic import analyse, parse_side
from reaction_builder.models import Reaction

GAMES = [
    ('guess-element', 'Guess the Element', 'Read the clues – atomic number, group, period, category – and name the element. 60 seconds.', 'atom', 3000),
    ('periodic-challenge', 'Periodic Table Challenge', 'Find each element on a blank periodic table. 10 rounds.', 'table', 1000),
    ('formula-match', 'Chemical Formula Matching', 'Match compound names with their formulas as fast as you can.', 'flask', 1500),
    ('weight-challenge', 'Molecular Weight Challenge', 'Pick the correct molar mass for each compound. 10 rounds.', 'calculator', 1500),
    ('memory', 'Chemistry Memory Game', 'Flip cards to match element symbols with their names.', 'sparkles', 1000),
    ('boiling-challenge', 'Boiling Point Challenge', 'Higher or lower? Guess which compound boils at a higher temperature.', 'thermo', 3000),
    ('timed-quiz', 'Timed Chemistry Quiz', 'Answer as many questions as you can in 60 seconds.', 'clock', 3000),
]
EXPERIMENTS = [
    ('titration', 'Acid–Base Titration', 'Add NaOH to HCl, watch the pH curve and find the equivalence point.', 'Acids & Bases', 'Real acids and alkalis are corrosive – wear goggles and gloves.'),
    ('flame-test', 'Flame Tests', 'Identify metal ions from the colour they give to a flame.', 'Analysis', 'Real flame tests need a Bunsen burner and supervision.'),
    ('ph-indicator', 'pH & Indicators', 'Test everyday solutions with universal indicator, litmus and phenolphthalein.', 'Acids & Bases', 'Never taste or mix household chemicals – bleach and ammonia release toxic gas.'),
    ('gas-laws', 'Gas Laws Lab', 'Change n, T and V and see the pressure from PV = nRT.', 'Physical Chemistry', ''),
    ('heating-curve', 'Heating Curve of Water', 'Add heat to ice and follow melting, warming and boiling.', 'Physical Chemistry', 'Steam causes severe burns.'),
]
WATER = {'atoms': [{'el': 'O', 'x': 480, 'y': 280}, {'el': 'H', 'x': 425, 'y': 320}, {'el': 'H', 'x': 535, 'y': 320}],
         'bonds': [{'a': 0, 'b': 1, 'order': 1}, {'a': 0, 'b': 2, 'order': 1}]}
CO2 = {'atoms': [{'el': 'O', 'x': 400, 'y': 280}, {'el': 'C', 'x': 480, 'y': 280}, {'el': 'O', 'x': 560, 'y': 280}],
       'bonds': [{'a': 0, 'b': 1, 'order': 2}, {'a': 1, 'b': 2, 'order': 2}]}


class Command(BaseCommand):
    help = 'Load elements, compounds, lessons, quiz questions, dictionary, reactions, games, experiments and demo users.'

    def add_arguments(self, parser):
        parser.add_argument('--no-demo', action='store_true', help='Skip demo users and their sample activity')

    @transaction.atomic
    def handle(self, *args, **opts):
        n = {}
        for e in load_seed('elements.json'):
            Element.objects.update_or_create(number=e['number'], defaults={k: v for k, v in e.items() if k != 'number'})
        n['elements'] = Element.objects.count()

        for c in load_seed('compounds.json'):
            c = dict(c)
            sol = c.pop('solubility', '')
            comp = composition(c['formula'])
            fields = {**c, 'molar_mass': comp['molar_mass']}
            # filter().first() rather than update_or_create: a user-added compound whose owner was
            # deleted also has added_by=None, and a duplicate name must not crash the deploy build.
            obj = Compound.objects.filter(name=c['name'], added_by=None).order_by('id').first()
            if obj:
                for k, v in fields.items():
                    setattr(obj, k, v)
                obj.save()
            else:
                obj = Compound.objects.create(added_by=None, **fields)
            obj.properties.all().delete()
            ChemicalProperty.objects.bulk_create([
                ChemicalProperty(compound=obj, name='Molar mass', value=f"{comp['molar_mass']} g/mol", note='calculated from IUPAC atomic weights'),
                ChemicalProperty(compound=obj, name='Elemental composition', value=', '.join(f"{r['element']} {r['percent']}%" for r in comp['rows']), note='by mass, calculated'),
                ChemicalProperty(compound=obj, name='Atoms per formula unit', value=str(comp['atoms'])),
                ChemicalProperty(compound=obj, name='Solubility in water', value=sol or 'Not available', note='qualitative, about 25 °C'),
            ])
        n['compounds'] = Compound.objects.filter(added_by=None).count()

        for l in load_seed('lessons.json'):
            Lesson.objects.update_or_create(slug=l['slug'], defaults={k: v for k, v in l.items() if k != 'slug'})
        n['lessons'] = Lesson.objects.count()

        for q in load_seed('quiz.json'):
            o = q['options']
            Question.objects.update_or_create(text=q['text'], defaults={
                'option_a': o[0], 'option_b': o[1], 'option_c': o[2], 'option_d': o[3], 'answer': q['answer'],
                'category': q['category'], 'difficulty': q['difficulty'], 'explanation': q['explanation']})
        n['questions'] = Question.objects.count()

        for t in load_seed('terms.json'):
            Term.objects.update_or_create(slug=t['slug'], defaults={k: v for k, v in t.items() if k != 'slug'})
        n['terms'] = Term.objects.count()

        for r in load_seed('reactions.json'):
            left, right = r['equation'].split('->')
            rx, px = parse_side(left), parse_side(right)
            info = analyse(rx, px)
            Reaction.objects.update_or_create(title=r['title'], is_sample=True, defaults={
                'user': None, 'reactants': rx, 'products': px, 'equation': info['equation'],
                'reaction_type': r['reaction_type'], 'conditions': r['conditions'], 'explanation': r['explanation'],
                'is_balanced': info['is_balanced'], 'is_public': True})
        n['sample reactions'] = Reaction.objects.filter(is_sample=True).count()

        for i, (slug, title, desc, icon, mx) in enumerate(GAMES, 1):
            Game.objects.update_or_create(slug=slug, defaults={'title': title, 'description': desc, 'icon': icon, 'max_points': mx, 'order': i})
        for i, (slug, title, summary, cat, safety) in enumerate(EXPERIMENTS, 1):
            Experiment.objects.update_or_create(slug=slug, defaults={'title': title, 'summary': summary, 'category': cat, 'safety_note': safety, 'order': i})
        n['games'], n['experiments'] = Game.objects.count(), Experiment.objects.count()

        if not opts['no_demo']:
            self._demo()
            n['demo users'] = 'demo / ChemDemo@2026, learner / Learner@2026'
        for k, v in n.items():
            self.stdout.write(f'  {k}: {v}')
        self.stdout.write(self.style.SUCCESS('CHEMVERSE data loaded.'))

    def _user(self, username, email, password, full_name, color):
        User = get_user_model()
        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.set_password(password)
            user.save()
        Profile.objects.update_or_create(user=user, defaults={'full_name': full_name, 'email_verified': True, 'avatar_color': color})
        return user, created

    def _demo(self):
        rnd = random.Random(42)
        demo, created = self._user('demo', 'demo@chemverse.local', 'ChemDemo@2026', 'Demo Learner', '#22d3ee')
        learner, created2 = self._user('learner', 'learner@chemverse.local', 'Learner@2026', 'Marie Learner', '#a78bfa')
        if not created and not created2:
            return  # demo activity already exists
        now = timezone.now()
        for user, skill, lessons in ((demo, 0.75, 6), (learner, 0.6, 3)):
            for l in Lesson.objects.all()[:lessons]:
                LessonProgress.objects.get_or_create(user=user, lesson=l)
            for i in range(7):
                total = 10
                score = max(2, min(10, round(total * skill + rnd.randint(-2, 2))))
                r = QuizResult.objects.create(user=user, category=rnd.choice(['', 'Elements', 'Reactions', 'Bonding']),
                                              difficulty=rnd.choice(['easy', 'medium']), score=score, total=total,
                                              percent=score * 10, duration_seconds=rnd.randint(90, 400))
                QuizResult.objects.filter(pk=r.pk).update(created_at=now - timedelta(days=14 - 2 * i))
            for g in Game.objects.all():
                for _ in range(2):
                    GameScore.objects.create(user=user, game=g, points=rnd.randint(int(g.max_points * .15), int(g.max_points * .55)))
            Profile.objects.filter(user=user).update(xp=rnd.randint(380, 620))
        Structure.objects.create(user=demo, name='Water', formula='H2O', molar_mass=18.015, data=WATER, is_public=True)
        Structure.objects.create(user=demo, name='Carbon dioxide', formula='CO2', molar_mass=44.009, data=CO2, is_public=True)
        for name in ('Water', 'Ethanol', 'Sodium chloride'):
            c = Compound.objects.filter(name=name, added_by=None).first()
            if c:
                FavoriteCompound.objects.get_or_create(user=demo, compound=c)
        for q, res in (('ethanol', 1), ('acid', 6), ('H2O', 2)):
            SearchHistory.objects.create(user=demo, query=q, results=res)
        rx = parse_side('2Na + Cl2')
        px = parse_side('2NaCl')
        info = analyse(rx, px)
        my_rx = Reaction.objects.create(user=demo, title='Sodium burns in chlorine', reactants=rx, products=px,
                                        equation=info['equation'], reaction_type='synthesis', conditions='Theoretical example',
                                        explanation='A very reactive metal and a reactive non-metal form an ionic salt.',
                                        is_balanced=info['is_balanced'])
        exp = Experiment.objects.filter(slug='titration').first()
        if exp:
            ExperimentLog.objects.create(user=demo, experiment=exp, result='Equivalence at 25.0 mL (0.10 M HCl vs 0.10 M NaOH)')
        p1 = Post.objects.create(author=demo, title='Why does ice float on water?', category='question',
                                 body='Most solids are denser than their liquids. Why is ice less dense than liquid water?')
        Comment.objects.create(post=p1, author=learner, body='Hydrogen bonds hold the molecules in an open hexagonal lattice in ice, so it takes up more space than the liquid.')
        p1.likes.add(learner)
        p2 = Post.objects.create(author=learner, title='My first balanced reaction', category='reaction', shared_reaction=my_rx,
                                 body='I built this in the Reaction Builder – the checker confirmed it is balanced!')
        p2.likes.add(demo)
        Post.objects.create(author=demo, title='Tip: use the Balancer step-by-step view', category='resource',
                            body='The balancer shows the equation for each element and how the fractions are cleared. Great for homework practice.')
        for label, url in (('Periodic Table', '/periodic-table/'), ('Compound Search', '/compounds/'), ('Structure Lab', '/structure-lab/'), ('Chemistry Games', '/games/')):
            Activity.objects.create(user=demo, kind='visit', label=label, url=url)
        Activity.objects.create(user=demo, kind='quiz', label='Quiz Mixed: 8/10 (80%)', url='/quiz/')
        Activity.objects.create(user=demo, kind='structure', label='Saved structure Water (H2O)', url='/structure-lab/')
