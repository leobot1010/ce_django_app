from django.urls import path, include
from . import views


# URLConf
urlpatterns = [
    path('home/', views.home, name='home'),

    # -------------- Scheme ------------- #
    path('scheme/', views.edit_scheme, name='scheme'),
    path('edit-scheme/', views.edit_scheme, name='edit_scheme'),

    # ------------ Participant -----------#
    path('view-participants/', views.view_participants, name='view_participants'),
    path('add-participants/', views.add_participants, name='add_participants'),

    path('edit-participants/<int:participant_id>/', views.add_participants, name='edit_participants'),
    path('edit-dates/<int:participant_id>/', views.edit_participant_dates, name='edit_participant_dates'),


    path('delete-participants/', views.delete_participants, name='delete_participants'),
    # path('delete-participant/<int:participant_id>/', views.delete_participant, name='delete_participant'),


    # ------------ Department ----------- #
    # path("manage-departments/", views.manage_departments, name="manage_departments"),
    path("manage-departments/", views.manage_departments, name="manage_departments"),


    # ------------- Holidays ------------ #
    path('holiday_summary', views.holiday_summary, name='holiday_summary')
]

