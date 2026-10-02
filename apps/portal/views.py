from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Max, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.website.models import Project, ProjectImage, ProjectTranslation

from .forms import ProjectCreateForm, ProjectEditForm

PROJECTS_PER_PAGE = 10


def _uploaded_images(files):
    """Return list of uploaded files from a multi-file input named gallery."""
    return [f for f in files.getlist('gallery') if f]


def _save_english(project, title, description):
    title = (title or '').strip()
    description = (description or '').strip()
    english = project.en_translation()
    if not title:
        if english:
            english.delete()
        return
    if english:
        english.title = title
        english.description = description
        english.status = ProjectTranslation.Status.APPROVED
        english.save()
        return
    ProjectTranslation.objects.create(
        project=project,
        language=ProjectTranslation.Language.EN,
        title=title,
        description=description,
        status=ProjectTranslation.Status.APPROVED,
    )


def _next_image_sort(project):
    current = project.images.aggregate(m=Max('sort_order'))['m']
    return (current or 0) + 1


def login_view(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('portal:dashboard')
        error = _('Pogrešno korisničko ime ili lozinka.')

    return render(request, 'portal/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('website:home')


@login_required
def dashboard(request):
    project_count = Project.objects.count()
    with_english = ProjectTranslation.objects.filter(
        language=ProjectTranslation.Language.EN,
    ).exclude(title='').count()
    return render(request, 'portal/dashboard.html', {
        'project_count': project_count,
        'with_english': with_english,
    })


@login_required
def project_list(request):
    projects = (
        Project.objects.prefetch_related(
            'translations',
            Prefetch('images', queryset=ProjectImage.objects.order_by('sort_order', 'id')),
        )
        .order_by('sort_order', 'id')
    )
    page = Paginator(projects, PROJECTS_PER_PAGE).get_page(request.GET.get('page'))
    return render(request, 'portal/projects/list.html', {
        'projects': page.object_list,
        'page_obj': page,
    })


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectCreateForm(request.POST, request.FILES)
        if form.is_valid():
            max_order = Project.objects.aggregate(m=Max('sort_order'))['m'] or 0
            project = Project.objects.create(
                sort_order=max_order + 1,
                is_published=form.cleaned_data['is_published'],
            )
            ProjectTranslation.objects.create(
                project=project,
                language=ProjectTranslation.Language.SR_LATN,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                status=ProjectTranslation.Status.SOURCE,
            )
            _save_english(
                project,
                form.cleaned_data['title_en'],
                form.cleaned_data['description_en'],
            )
            main = ProjectImage(project=project, is_main=True, sort_order=0)
            main.image = form.cleaned_data['image']
            main.save()

            for index, uploaded in enumerate(_uploaded_images(request.FILES), start=1):
                img = ProjectImage(project=project, is_main=False, sort_order=index)
                img.image = uploaded
                img.save()

            messages.success(request, 'Projekat je dodat.')
            return redirect('portal:project_edit', pk=project.pk)
    else:
        form = ProjectCreateForm()

    return render(request, 'portal/projects/form.html', {
        'form': form,
        'page_title': 'Novi projekat',
        'submit_label': 'Sačuvaj projekat',
    })


@login_required
def project_edit(request, pk):
    project = get_object_or_404(
        Project.objects.prefetch_related('translations', 'images'),
        pk=pk,
    )
    sr = project.sr_translation()
    en = project.en_translation()

    if request.method == 'POST':
        action = request.POST.get('action', 'save')

        if action == 'set_main':
            image = get_object_or_404(ProjectImage, pk=request.POST.get('image_id'), project=project)
            image.is_main = True
            image.save()
            messages.success(request, 'Glavna slika je promenjena.')
            return redirect('portal:project_edit', pk=project.pk)

        if action == 'delete_image':
            image = get_object_or_404(ProjectImage, pk=request.POST.get('image_id'), project=project)
            was_main = image.is_main
            image.delete()
            if was_main:
                replacement = project.images.order_by('sort_order', 'id').first()
                if replacement:
                    replacement.is_main = True
                    replacement.save(update_fields=['is_main'])
            messages.success(request, 'Slika je obrisana.')
            return redirect('portal:project_edit', pk=project.pk)

        form = ProjectEditForm(request.POST, request.FILES)
        if form.is_valid():
            project.is_published = form.cleaned_data['is_published']
            project.save(update_fields=['is_published', 'updated_at'])

            if sr:
                sr.title = form.cleaned_data['title']
                sr.description = form.cleaned_data['description']
                sr.save()
            else:
                ProjectTranslation.objects.create(
                    project=project,
                    language=ProjectTranslation.Language.SR_LATN,
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data['description'],
                    status=ProjectTranslation.Status.SOURCE,
                )
            _save_english(
                project,
                form.cleaned_data['title_en'],
                form.cleaned_data['description_en'],
            )

            sort = _next_image_sort(project)
            for uploaded in _uploaded_images(request.FILES):
                img = ProjectImage(
                    project=project,
                    is_main=not project.images.exists(),
                    sort_order=sort,
                )
                img.image = uploaded
                img.save()
                sort += 1

            messages.success(request, 'Projekat je sačuvan.')
            return redirect('portal:project_edit', pk=project.pk)
    else:
        form = ProjectEditForm(initial={
            'title': sr.title if sr else '',
            'description': sr.description if sr else '',
            'title_en': en.title if en else '',
            'description_en': en.description if en else '',
            'is_published': project.is_published,
        })

    return render(request, 'portal/projects/form.html', {
        'form': form,
        'project': project,
        'page_title': 'Izmena projekta',
        'submit_label': 'Sačuvaj izmene',
    })


@login_required
def project_translate(request, pk):
    return redirect('portal:project_edit', pk=pk)


@login_required
@require_POST
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    messages.success(request, 'Projekat je obrisan.')
    return redirect('portal:project_list')
