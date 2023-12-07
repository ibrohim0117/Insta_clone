from django.urls import path

from post.views import PostListApiView

urlpatterns = [
    path('posts/', PostListApiView.as_view())
]

