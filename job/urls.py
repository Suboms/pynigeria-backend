from django.urls import path
from .apis import JobPostingCreateView, JobPostingDetailView, JobPostingListView, JobPostingUpdateView, JobPostingDeleteView


urlpatterns = [
    path('', JobPostingListView.as_view(), name='job-posting-list'),
    path('postings/', JobPostingCreateView.as_view(), name='job-posting-create'),
    path('postings/<slug:slug>/', JobPostingDetailView.as_view(), name='job-posting-detail'),
    path('postings/<int:pk>/update', JobPostingUpdateView.as_view(), name='job-posting-upate'),
    path('postings/<int:pk>/delete', JobPostingDeleteView.as_view(), name='job-posting-delete'),
    
]
