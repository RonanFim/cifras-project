from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chord/<int:pk>/', views.chordsPage, name='chords'),
    # path('post/new/', views.post_new, name='post_new'),
    # path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
]
