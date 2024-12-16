from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q


from .models import JobPosting
from .permissions import IsJobPoster
from .serializers import JobPostingSerializer


class JobPostingCreateView(APIView):
    """
    View to list all job postings or create a new job posting.
    """
    permission_classes = [IsJobPoster ]
    def post(self, request):
        serializer = JobPostingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class JobPostingUpdateView(APIView):
    permission_classes = [IsJobPoster]

    def get_object(self, pk):
        try:
            return JobPosting.objects.get(pk=pk)
        except JobPosting.DoesNotExist:
            return None
    
    def put(self, request, pk):
        job_posting = self.get_object(pk)
        if job_posting is None:
            return Response({"error": "Job posting not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = JobPostingSerializer(job_posting, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobPostingDeleteView(APIView):
    permission_classes = [IsJobPoster]

    def get_object(self, pk):
        try:
            return JobPosting.objects.get(pk=pk)
        except JobPosting.DoesNotExist:
            return None
    def delete(self, request, pk):
        job_posting = self.get_object(pk)
        if job_posting is None:
            return Response({"error": "Job posting not found"}, status=status.HTTP_404_NOT_FOUND)
        job_posting.delete()
        return Response({"message": "Job posting deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class JobPostingListView(APIView):
    """
    View to list job postings with optional search filters.
    The search parameter can be used to filter job postings by title, company name, location, or skills.
    """
    permission_classes = []
    def get(self, request):
        title = request.query_params.get('title', '')
        role = request.query_params.get('role', '')
        location = request.query_params.get('location', '')
        company_name = request.query_params.get('company_name', '')
        skills = request.query_params.get('skills', '')
        jobs = JobPosting.objects.all()
        filters = Q()
        if title:
            filters &= Q(title__icontains=title)
        if role:
            filters &= Q(job_type__icontains=role)
        if location:
            filters &= Q(location__icontains=location)
        if company_name:
            filters &= Q(company_name__icontains=company_name)
        if skills:
            filters &= Q(skills_required__icontains=skills)
        #  check if any filter applies
        if filters:
            jobs = jobs.filter(filters)
           
        

        # Serialize the filtered job postings
        serializer = JobPostingSerializer(jobs, many=True)

        # Return the filtered job postings
        return Response(serializer.data, status=status.HTTP_200_OK)


class JobPostingDetailView(APIView):
    """
    View to retrieve, update, or delete a specific job posting.
    """
    permission_classes = []

    def get_object(self, slug):
        try:
            return JobPosting.objects.get(slug=slug)
        except JobPosting.DoesNotExist:
            return None

    def get(self, request, slug):
        job_posting = self.get_object(slug)
        if job_posting is None:
            return Response({"error": "Job posting not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = JobPostingSerializer(job_posting)
        return Response(serializer.data, status=status.HTTP_200_OK)