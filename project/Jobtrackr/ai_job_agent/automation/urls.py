from django.urls import path
from .views import (
    CoverLetterListView, CoverLetterGenerateView, 
    CoverLetterDetailView, CoverLetterDeleteView,
    AssistedApplyView
)

app_name = 'automation'

urlpatterns = [
    path('cover-letters/', CoverLetterListView.as_view(), name='cover_letter_list'),
    path('cover-letters/generate/', CoverLetterGenerateView.as_view(), name='cover_letter_generate'),
    path('cover-letters/<int:pk>/', CoverLetterDetailView.as_view(), name='cover_letter_detail'),
    path('cover-letters/<int:pk>/delete/', CoverLetterDeleteView.as_view(), name='cover_letter_delete'),
    path('assisted-apply/', AssistedApplyView.as_view(), name='assisted_apply'),
]
