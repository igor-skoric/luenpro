from django.urls import path

from . import views

app_name = 'portal'

urlpatterns = [
    path('prijava/', views.login_view, name='login'),
    path('odjava/', views.logout_view, name='logout'),
    path('app/', views.dashboard, name='dashboard'),
    path('app/projekti/', views.project_list, name='project_list'),
    path('app/projekti/novi/', views.project_create, name='project_create'),
    path('app/projekti/<int:pk>/', views.project_edit, name='project_edit'),
    path('app/projekti/<int:pk>/prevod/', views.project_translate, name='project_translate'),
    path('app/projekti/<int:pk>/obrisi/', views.project_delete, name='project_delete'),
]
