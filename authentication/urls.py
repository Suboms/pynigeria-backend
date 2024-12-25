from django.urls import path

from .views import (
    GetQRCodeView,
    RegisterView,
    TOTPDeviceCreateView,
    VerifyEmailBeginView,
    VerifyEmailCompleteView,
    VerifyTOTPDeviceView,
)

app_name = "authentication"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "verify-email/begin/", VerifyEmailBeginView.as_view(), name="verify-email-begin"
    ),
    path(
        "verify-email/complete/<str:token>/",
        VerifyEmailCompleteView.as_view(),
        name="verify-email-complete",
    ),
    path(
        "totp-device/create/", TOTPDeviceCreateView.as_view(), name="create-totp-device"
    ),
    path("totp-device/qrcode/", GetQRCodeView.as_view(), name="get-qr-code"),
    path(
        "totp-device/verify/", VerifyTOTPDeviceView.as_view(), name="verify-totp-device"
    ),
]
