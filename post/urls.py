from django.urls import path

from post.views import PostListApiView, PostCreateView, PostRetrieveUpdateDestroyView, PostLikeListView, \
    PostCommentListView, PostCommentCreateView, CommentRetrieveApiView, CommentLikeListApiView

urlpatterns = [
    path('list/', PostListApiView.as_view()),
    path('create/', PostCreateView.as_view()),
    path('<uuid:pk>/', PostRetrieveUpdateDestroyView.as_view()),
    path('<uuid:pk>/likes/', PostLikeListView.as_view()),
    path('<uuid:pk>/comments/', PostCommentListView.as_view()),
    path('<uuid:pk>/comments/create/', PostCommentCreateView.as_view()),

    path('comments/<uuid:pk>/', CommentRetrieveApiView.as_view()),
    path('comments/<uuid:pk>/likes', CommentLikeListApiView.as_view()),
]

