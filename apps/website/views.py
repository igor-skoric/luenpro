import json

from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import ngettext

from .models import Project, ProjectImage

PROJECTS_PER_PAGE = 6


def _serialize_projects():
    language = get_language() or 'sr-latn'
    projects_qs = (
        Project.objects.filter(is_published=True)
        .prefetch_related(
            'translations',
            Prefetch('images', queryset=ProjectImage.objects.order_by('sort_order', 'id')),
        )
        .order_by('sort_order', 'id')
    )

    projects = []
    for project in projects_qs:
        images = list(project.images.all())
        if not images:
            continue
        main = next((img for img in images if img.is_main), images[0])
        gallery = [img.image.url for img in images]
        count = len(images)
        title = project.get_title(language)
        description = project.get_description(language)
        projects.append({
            'id': project.pk,
            'title': title,
            'location': description,
            'cover_url': main.image.url,
            'images': gallery,
            'photo_count_label': ngettext(
                '%(count)d fotografija',
                '%(count)d fotografija',
                count,
            ) % {'count': count},
        })
    return projects


def home(request):
    return render(request, 'website/home.html')


def projekti(request):
    projects = _serialize_projects()
    page = Paginator(projects, PROJECTS_PER_PAGE).get_page(request.GET.get('page'))
    current = list(page.object_list)
    portfolio_json = json.dumps(
        [
            {
                'id': p['id'],
                'title': p['title'],
                'location': p['location'],
                'cover': p['cover_url'],
                'images': p['images'],
            }
            for p in current
        ],
        ensure_ascii=False,
    )
    return render(request, 'website/projekti.html', {
        'projects': current,
        'page_obj': page,
        'portfolio_json': portfolio_json,
    })


def _redirect_to_section(section_id):
    return redirect(reverse('website:home') + f'#{section_id}')


def about(request):
    return _redirect_to_section('o-nama')


def contact(request):
    return redirect('website:home')


def faq(request):
    return redirect('website:home')


def services(request):
    return _redirect_to_section('usluge')
