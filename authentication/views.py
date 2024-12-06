from rest_framework.views import APIView
from .serializers import RegisterSerializer, ValidationError, IntegrityError
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import Throttled
from drf_spectacular.utils import extend_schema


class RegisterView(APIView):
    serializer_class = RegisterSerializer
    throttle_classes = [AnonRateThrottle]

    @extend_schema(operation_id="v1_register", tags=["auth_v1"])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                new_user_data = serializer.save()
                response_data = self.serializer_class(new_user_data).data
                return Response({"data": response_data}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"detail": str(e.detail["error"][0])}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Throttled:
            pass
