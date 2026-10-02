from django.conf import settings
from django.db import models
from django.utils.translation import get_language


class Project(models.Model):
    sort_order = models.PositiveIntegerField('redosled', default=0, db_index=True)
    is_published = models.BooleanField('objavljeno', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'projekat'
        verbose_name_plural = 'projekti'

    def __str__(self):
        return self.get_title() or f'Project #{self.pk}'

    def translation_for(self, language=None, *, require_approved=False):
        language = language or get_language() or settings.LANGUAGE_CODE
        translations = {t.language: t for t in self.translations.all()}
        chosen = translations.get(language)
        if (
            require_approved
            and chosen
            and language != ProjectTranslation.Language.SR_LATN
            and chosen.status != ProjectTranslation.Status.APPROVED
        ):
            chosen = None
        return (
            chosen
            or translations.get(settings.LANGUAGE_CODE)
            or next(iter(translations.values()), None)
        )

    def _translation(self, language=None):
        lang = language or get_language()
        return self.translation_for(language, require_approved=(lang == 'en'))

    def get_title(self, language=None):
        tr = self._translation(language)
        return tr.title if tr else ''

    def get_description(self, language=None):
        tr = self._translation(language)
        return tr.description if tr else ''

    def sr_translation(self):
        return self.translations.filter(language=ProjectTranslation.Language.SR_LATN).first()

    def en_translation(self):
        return self.translations.filter(language=ProjectTranslation.Language.EN).first()

    @property
    def main_image(self):
        return self.images.filter(is_main=True).first() or self.images.order_by('sort_order', 'id').first()

    @property
    def gallery_images(self):
        return self.images.order_by('sort_order', 'id')


class ProjectTranslation(models.Model):
    class Language(models.TextChoices):
        SR_LATN = 'sr-latn', 'Srpski'
        EN = 'en', 'English'

    class Status(models.TextChoices):
        SOURCE = 'source', 'Izvorni jezik'
        DRAFT = 'draft', 'Nacrt'
        PENDING = 'pending', 'Na odobrenju'
        APPROVED = 'approved', 'Odobreno'
        REJECTED = 'rejected', 'Odbačeno'

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name='projekat',
    )
    language = models.CharField('jezik', max_length=10, choices=Language.choices)
    title = models.CharField('naziv', max_length=255)
    description = models.CharField('opis', max_length=500, blank=True)
    status = models.CharField(
        'status prevoda',
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'language'],
                name='unique_project_language',
            ),
        ]
        verbose_name = 'prevod projekta'
        verbose_name_plural = 'prevodi projekata'

    def __str__(self):
        return f'{self.title} ({self.language})'

    def save(self, *args, **kwargs):
        if self.language == self.Language.SR_LATN:
            self.status = self.Status.SOURCE
        super().save(*args, **kwargs)


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='projekat',
    )
    image = models.ImageField('slika', upload_to='projects/')
    is_main = models.BooleanField('glavna slika', default=False)
    sort_order = models.PositiveIntegerField('redosled', default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'slika projekta'
        verbose_name_plural = 'slike projekata'

    def __str__(self):
        label = 'main' if self.is_main else 'gallery'
        return f'{self.project_id} — {label} #{self.pk}'

    def save(self, *args, **kwargs):
        if self.is_main and self.project_id:
            ProjectImage.objects.filter(project_id=self.project_id, is_main=True).exclude(
                pk=self.pk
            ).update(is_main=False)
        super().save(*args, **kwargs)
        if self.project_id and not self.project.images.filter(is_main=True).exists():
            first = self.project.images.order_by('sort_order', 'id').first()
            if first and not first.is_main:
                ProjectImage.objects.filter(pk=first.pk).update(is_main=True)
