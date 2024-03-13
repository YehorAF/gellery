from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from gallery import views

urlpatterns = [
    path("", views.get_pictures),
    path("login", views.get_login_page),
    path("signin", views.signin),
    path("auth", views.auth),
    path("logout", views.logout),
    path("users", views.get_users),
    path("users/<str:username>", views.get_user),
    path("users/<str:username>/follow", views.follow),
    path("load", views.get_load_page),
    path("upload", views.upload_picture),
    path("users/<str:username>/pictures/<int:picture_id>", views.get_picture),
    path("users/<str:username>/pictures/<int:picture_id>/load", views.load_picture),
    path("users/<str:username>/pictures/<int:picture_id>/react", views.react)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)