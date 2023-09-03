from django.urls import path

from users.views import UserCreateView, ManageUserView

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="create"),
    path("me/", ManageUserView.as_view(), name="manage"),
]

app_name = "users"
