from  django.urls import path
from .views import CreateUserView, TokenView , ManagerUserView

app_name="user" # use for reverse url in testing.

urlpatterns = [
    path("create/",CreateUserView.as_view(),name="create"),
    path('token/',TokenView.as_view(),name='token'),
    path('me/',ManagerUserView.as_view(),name='me')
]
