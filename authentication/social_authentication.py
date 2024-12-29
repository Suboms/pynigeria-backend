from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from social_core.utils import (
    partial_pipeline_data,
    user_is_active,
    user_is_authenticated,
)

from .serializers import UserSerializer


def complete_social_authentication(request, backend):
    backend = request.backend
    user = request.user

    # Check if user is authenticated
    is_user_authenticated = user_is_authenticated(user)
    user = user if is_user_authenticated else None

    # Complete any partial authentication or perform a full one
    partial = partial_pipeline_data(backend, user)
    if partial:
        user = backend.continue_pipeline(partial)
        backend.clean_partial_pipeline(partial.token)
    else:
        user = backend.complete(user=user)

    user_model = backend.strategy.storage.user.user_model()
    if user and not isinstance(user, user_model):
        raise AuthenticationFailed("Provided 'user' is not a valid User object.")
    if user:
        if user_is_active(user):
            is_new = getattr(user, "is_new", False)
            if is_new:
                user_data = UserSerializer(user).data
                user_data["message"] = "Proceed to 2FA setup."
                return Response({"data": user_data}, status=status.HTTP_201_CREATED)
            else:
                if not user.is_2fa_enabled:
                    raise AuthenticationFailed(
                        "2FA setup must be completed before login."
                    )
                else:
                    refresh_token = RefreshToken.for_user(user)
                    access_token = refresh_token.access_token
                    return Response(
                        {
                            "data": dict(
                                id=user.id,
                                email=user.email,
                                access=str(access_token),
                                refresh=str(refresh_token),
                            )
                        },
                        status=status.HTTP_200_OK,
                    )
        else:
            raise AuthenticationFailed("This account is inactive.")
