from django.shortcuts import render
from rest_framework.response import Response

from shared.custom_pagination import CustomPagination
from .models import Post, PostLike, PostComment
from .serializers import PostSerializer, PostLikeSerializer, CommentSerializer, CommentLikeSerializer
from rest_framework import generics, permissions, status


class PostListApiView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    pagination_class = CustomPagination


class PostCreatApiView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'success': True,
                'code': status.HTTP_200_OK,
                'message': "Post muvofaqiyatli o'zgardi",
                'data': serializer.data

            }
        )

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return Response(
            {
                'success': True,
                'code': status.HTTP_204_NO_CONTENT,
                'message': "Post muvofaqiyatli o'chirildi"
            }
        )


class PostCommentList(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = (permissions.AllowAny, )

    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostComment.objects.filter(post_id=post_id)
        return queryset


class PostCommentCreateApiView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        serializer.save(author=self.request.user, post_id=post_id)


# class CommentCreateApiView(generics.CreateAPIView):
#     serializer_class = CommentSerializer
#     permission_classes = (permissions.IsAuthenticated, )
#
#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)
