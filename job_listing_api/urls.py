from django.urls import include, path
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenObtainPairView

from job_listing_api.views import (
    BookmarkFolderViewset,
    BookmarkViewset,
    JobApproveView,
    JobViewset,
)

router = DefaultRouter()

router.register(r"job", JobViewset)
router.register(r"bookmark", BookmarkViewset)
router.register(r"bookmark-folders", BookmarkFolderViewset)


urlpatterns = [
    path("", include(router.urls)),
    path("job/approve/<slug:slug>/", JobApproveView.as_view(), name="job-approve"),
    path("login/", TokenObtainPairView.as_view())
]
