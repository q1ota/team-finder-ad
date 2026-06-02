from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import Skill, User


SKILLS_DATA = [
    'Python', 'Django', 'JavaScript', 'React', 'Vue.js',
    'TypeScript', 'PostgreSQL', 'Docker', 'Git', 'REST API',
    'HTML/CSS', 'Node.js', 'FastAPI', 'Redis', 'Figma',
]

USERS_DATA = [
    {
        'email': 'admin@teamfinder.ru',
        'name': 'Админ',
        'surname': 'Иванов',
        'password': 'admin123',
        'is_staff': True,
        'is_superuser': True,
        'about': 'Администратор платформы TeamFinder.',
        'skills': ['Python', 'Django', 'PostgreSQL', 'Docker'],
    },
    {
        'email': 'alice@example.com',
        'name': 'Алиса',
        'surname': 'Смирнова',
        'password': 'password123',
        'about': 'Fullstack-разработчик с опытом 3 года.',
        'skills': ['Python', 'Django', 'React', 'PostgreSQL'],
    },
    {
        'email': 'bob@example.com',
        'name': 'Борис',
        'surname': 'Петров',
        'password': 'password123',
        'about': 'Frontend-разработчик, люблю создавать красивые интерфейсы.',
        'skills': ['JavaScript', 'React', 'TypeScript', 'HTML/CSS'],
    },
    {
        'email': 'carol@example.com',
        'name': 'Карина',
        'surname': 'Козлова',
        'password': 'password123',
        'about': 'Backend-разработчик, специализируюсь на микросервисах.',
        'skills': ['Python', 'FastAPI', 'Docker', 'Redis'],
    },
    {
        'email': 'david@example.com',
        'name': 'Дмитрий',
        'surname': 'Новиков',
        'password': 'password123',
        'about': 'DevOps-инженер и бэкенд-разработчик.',
        'skills': ['Docker', 'Git', 'PostgreSQL', 'Node.js'],
    },
]

PROJECTS_DATA = [
    {
        'owner_email': 'alice@example.com',
        'name': 'Платформа онлайн-обучения',
        'description': 'Создаём платформу для онлайн-курсов с видеолекциями, тестами и сертификатами. Ищем разработчиков фронтенда и дизайнера.',
        'status': 'open',
        'participants': ['bob@example.com'],
    },
    {
        'owner_email': 'bob@example.com',
        'name': 'Мобильное приложение для трекинга привычек',
        'description': 'Приложение для отслеживания полезных привычек с геймификацией и социальными функциями.',
        'status': 'open',
        'participants': ['alice@example.com', 'carol@example.com'],
    },
    {
        'owner_email': 'carol@example.com',
        'name': 'API для агрегации новостей',
        'description': 'Создаём микросервис для агрегации новостей из разных источников с возможностью персонализации ленты.',
        'status': 'open',
        'participants': ['david@example.com'],
    },
    {
        'owner_email': 'david@example.com',
        'name': 'Система мониторинга серверов',
        'description': 'Инструмент для мониторинга состояния серверов в реальном времени с алертами и дашбордами.',
        'status': 'closed',
        'participants': ['alice@example.com'],
    },
    {
        'owner_email': 'alice@example.com',
        'name': 'Чат-бот для HR-отдела',
        'description': 'Telegram-бот, который помогает HR автоматизировать первичный отбор кандидатов.',
        'status': 'open',
        'participants': [],
    },
    {
        'owner_email': 'carol@example.com',
        'name': 'Marketplace для фриланс-дизайнеров',
        'description': 'Платформа для поиска дизайнеров и размещения заказов с портфолио и рейтинговой системой.',
        'status': 'open',
        'participants': ['bob@example.com'],
    },
]


class Command(BaseCommand):
    help = 'Seed database with test data'

    def handle(self, *args, **options):
        self.stdout.write('Creating skills...')
        skill_objs = {}
        for name in SKILLS_DATA:
            skill, _ = Skill.objects.get_or_create(name=name)
            skill_objs[name] = skill

        self.stdout.write('Creating users...')
        user_objs = {}
        for u in USERS_DATA:
            if User.objects.filter(email=u['email']).exists():
                user_objs[u['email']] = User.objects.get(email=u['email'])
                self.stdout.write(f"  User {u['email']} already exists, skipping.")
                continue
            user = User.objects.create_user(
                email=u['email'],
                name=u['name'],
                surname=u['surname'],
                password=u['password'],
                about=u.get('about', ''),
                is_staff=u.get('is_staff', False),
                is_superuser=u.get('is_superuser', False),
            )
            for skill_name in u.get('skills', []):
                user.skills.add(skill_objs[skill_name])
            user_objs[u['email']] = user
            self.stdout.write(f'  Created user: {user.email}')

        self.stdout.write('Creating projects...')
        for p in PROJECTS_DATA:
            owner = user_objs.get(p['owner_email'])
            if not owner:
                continue
            if Project.objects.filter(name=p['name'], owner=owner).exists():
                self.stdout.write(f"  Project '{p['name']}' already exists, skipping.")
                continue
            project = Project.objects.create(
                name=p['name'],
                description=p['description'],
                owner=owner,
                status=p['status'],
            )
            project.participants.add(owner)
            for email in p.get('participants', []):
                participant = user_objs.get(email)
                if participant:
                    project.participants.add(participant)
            self.stdout.write(f"  Created project: {project.name}")

        self.stdout.write(self.style.SUCCESS('\nSeed data created successfully!'))
        self.stdout.write('\nTest accounts:')
        for u in USERS_DATA:
            self.stdout.write(f'  {u["email"]} / {u["password"]}')
