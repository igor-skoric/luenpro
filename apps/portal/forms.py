from django import forms


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class ProjectCreateForm(forms.Form):
    title = forms.CharField(
        label='Naziv',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'npr. ASICS — Iskra Trail',
        }),
    )
    description = forms.CharField(
        label='Opis',
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'input input--textarea',
            'rows': 3,
            'placeholder': 'npr. Kosmaj, Srbija · 2025–2026.',
        }),
    )
    image = forms.ImageField(
        label='Glavna slika',
        widget=forms.FileInput(attrs={
            'class': 'input-file-native',
            'accept': 'image/*',
        }),
    )
    gallery = forms.FileField(
        label='Dodatne slike',
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'input-file-native',
            'accept': 'image/*',
        }),
    )
    title_en = forms.CharField(
        label='Naziv (EN)',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'e.g. ASICS — Iskra Trail',
        }),
    )
    description_en = forms.CharField(
        label='Opis (EN)',
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'input input--textarea',
            'rows': 3,
            'placeholder': 'e.g. Kosmaj, Serbia · 2025–2026.',
        }),
    )
    is_published = forms.BooleanField(label='Objavi na sajtu', required=False, initial=True)

    def clean(self):
        cleaned = super().clean()
        _require_english_title(self, cleaned)
        return cleaned


class ProjectEditForm(forms.Form):
    title = forms.CharField(
        label='Naziv',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'npr. ASICS — Iskra Trail',
        }),
    )
    description = forms.CharField(
        label='Opis',
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'input input--textarea',
            'rows': 3,
            'placeholder': 'npr. Kosmaj, Srbija · 2025–2026.',
        }),
    )
    title_en = forms.CharField(
        label='Naziv (EN)',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'e.g. ASICS — Iskra Trail',
        }),
    )
    description_en = forms.CharField(
        label='Opis (EN)',
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'input input--textarea',
            'rows': 3,
            'placeholder': 'e.g. Kosmaj, Serbia · 2025–2026.',
        }),
    )
    gallery = forms.FileField(
        label='Dodaj još slika',
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'input-file-native',
            'accept': 'image/*',
        }),
    )
    is_published = forms.BooleanField(label='Objavi na sajtu', required=False)

    def clean(self):
        cleaned = super().clean()
        _require_english_title(self, cleaned)
        return cleaned


def _require_english_title(form, cleaned):
    description = (cleaned.get('description_en') or '').strip()
    title = (cleaned.get('title_en') or '').strip()
    if description and not title:
        form.add_error('title_en', 'Unesite engleski naziv ako unosite opis.')
