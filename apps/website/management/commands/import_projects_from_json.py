import json
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from apps.website.models import Project, ProjectImage, ProjectTranslation


class Command(BaseCommand):
    help = 'Import projects from apps/website/data/projects.json into the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing projects before import.',
        )

    def handle(self, *args, **options):
        json_path = Path(settings.BASE_DIR) / 'apps' / 'website' / 'data' / 'projects.json'
        static_projects = Path(settings.BASE_DIR) / 'static' / 'img' / 'projects'

        if not json_path.exists():
            self.stderr.write(self.style.ERROR(f'Missing {json_path}'))
            return

        if options['clear']:
            Project.objects.all().delete()
            self.stdout.write('Cleared existing projects.')

        data = json.loads(json_path.read_text(encoding='utf-8'))
        created = 0

        for index, item in enumerate(data):
            project = Project.objects.create(
                sort_order=index,
                is_published=True,
            )
            ProjectTranslation.objects.create(
                project=project,
                language=ProjectTranslation.Language.SR_LATN,
                title=item['title'],
                description=item.get('location', ''),
            )

            cover_name = Path(item['cover']).name
            cover_src = static_projects / cover_name
            if cover_src.exists():
                with cover_src.open('rb') as fh:
                    image = ProjectImage(project=project, is_main=True, sort_order=0)
                    image.image.save(cover_name, File(fh), save=True)

            for img_index, img_path in enumerate(item.get('images', []), start=1):
                name = Path(img_path).name
                src = static_projects / name
                if not src.exists():
                    self.stderr.write(self.style.WARNING(f'Missing image: {src}'))
                    continue
                with src.open('rb') as fh:
                    image = ProjectImage(project=project, is_main=False, sort_order=img_index)
                    image.image.save(name, File(fh), save=True)

            created += 1
            self.stdout.write(f'  + [{item["id"]}] imported')

        self.stdout.write(self.style.SUCCESS(f'Imported {created} projects.'))
