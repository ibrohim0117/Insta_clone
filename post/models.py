from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.db import models
from django.db.models import UniqueConstraint

from shared.models import BaseModel
from user.models import User


class Post(models.Model, BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='post_images/', validators=[FileExtensionValidator(allowed_extensions=['jpeg', 'png', 'jpg'])])
    caption = models.TextField(validators=[MaxLengthValidator(2000)])

    class Meta:
        db_table = 'posts'
        verbose_name = 'post'
        verbose_name_plural = 'posts'


class PostComment(models.Model, BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment = models.CharField(max_length=500)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='child',
        null=True,
        blank=True
    )


class PostLike(BaseModel, models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    class Meta:       # cheklovlar bir marta like bosgan odam boshqa bosolmasligi haqida!
        constraints = [
            UniqueConstraint(
                fields=['author', 'post']
            )
        ]


class CommentLike(models.Model, BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='likes')

    class Meta:  # cheklovlar bir odam bir commentga bir marta like bosgan odam boshqa bosolmasligi haqida!
        constraints = [
            UniqueConstraint(
                fields=['author', 'comment']
            )
        ]


