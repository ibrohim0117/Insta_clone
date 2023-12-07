from django.urls import path

from post.views import PostListApiView, PostCreatApiView, PostRetrieveUpdateDestroyAPIView, PostCommentList, \
    PostCommentCreateApiView

urlpatterns = [
    path('posts/', PostListApiView.as_view()),
    path('create/', PostCreatApiView.as_view()),
    path('post/<uuid:pk>/', PostRetrieveUpdateDestroyAPIView.as_view()),
    path('post/<uuid:pk>/comments/create/', PostCommentCreateApiView.as_view()),
]

