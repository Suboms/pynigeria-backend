from django.urls import path
from .apis import JobPostingCreateView, JobPostingDetailView, JobPostingListView, JobPostingUpdateView, JobPostingDeleteView

app_name = "job"

urlpatterns = [
    path('', JobPostingListView.as_view(), name='job_posting_list'),
    path('postings/', JobPostingCreateView.as_view(), name='job_posting_create'),
    path('postings/<slug:slug>/', JobPostingDetailView.as_view(), name='job_posting_detail'),
    path('postings/<int:pk>/update', JobPostingUpdateView.as_view(), name='job_posting_upate'),
    path('postings/<int:pk>/delete', JobPostingDeleteView.as_view(), name='job_posting_delete'),
    
]
