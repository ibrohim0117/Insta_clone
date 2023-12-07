from django.shortcuts import render

from shared.custom_pagination import CustomPagination
from .models import Post, PostLike, PostComment
from .serializers import PostSerializer, PostLikeSerializer, CommentSerializer, CommentLikeSerializer
from rest_framework import generics, permissions


class PostListApiView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    pagination_class = CustomPagination

