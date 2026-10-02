from django.urls import path

from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('projekti/', views.projekti, name='projekti'),
    path('o-nama/', views.about, name='about'),
    path('kontakt/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('usluge/', views.services, name='services'),
]
