from django.urls import path, include
from . import views

# URLConf
urlpatterns = [
    path('home/', views.home, name='home'),
    path('scheme/', views.scheme, name='scheme'),
    path('edit-scheme/', views.edit_scheme, name='edit_scheme'),
    path('view-participants/', views.view_participants, name='view_participants'),
    path('add-participants/', views.add_participants, name='add_participants'),
    path('edit-participants/', views.edit_participants, name='edit_participants'),
    path('edit-departments/', views.edit_departments, name='edit_departments'),
    path('delete-departments/<int:pk>/', views.delete_departments, name='delete_departments'),
    path('holiday_summary', views.holiday_summary, name='holiday_summary')
]

