from urllib.parse import urlsplit

from django.utils import translation
from django.views.i18n import set_language as django_set_language


def set_language(request):
    """Switch language, including back to the unprefixed default language.

    LocaleMiddleware treats every unprefixed path as Serbian, including
    /i18n/setlang/. Django can only translate a prefixed URL such as
    /en/projekti/ while that language is active, so activate it first.
    """
    next_url = request.POST.get('next', request.GET.get('next'))
    if next_url:
        lang_from_next = translation.get_language_from_path(urlsplit(next_url).path)
        if lang_from_next:
            translation.activate(lang_from_next)
            request.LANGUAGE_CODE = lang_from_next
    return django_set_language(request)
