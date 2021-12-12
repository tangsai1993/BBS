from django.db import models

# Create your models here.


from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    """
    用户信息
    """
    nid = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=11, null=True, unique=True)
    avatar = models.FileField(upload_to='avatars/', default="avatars/default.png")
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    blog = models.OneToOneField(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username


class Blog(models.Model):
    """
    博客信息
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    site_name = models.CharField(verbose_name='站点名称', max_length=64)
    theme = models.CharField(verbose_name='博客主题', max_length=32)

    def __str__(self):
        return self.title


class Category(models.Model):
    """
    博主个人文章分类表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Article(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章描述')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    content = models.TextField()

    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)

    user = models.ForeignKey(verbose_name='作者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    category = models.ForeignKey(to='Category', to_field='nid', null=True, on_delete=models.CASCADE)
    tags = models.ManyToManyField(
        to="Tag",
        through='Article2Tag',
        through_fields=('article', 'tag'),
    )

    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='文章', to="Article", to_field='nid', on_delete=models.CASCADE)
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid', on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ('article', 'tag'),
        ]

    def __str__(self):
        v = self.article.title + "---" + self.tag.title
        return v


class ArticleUpDown(models.Model):
    """
    点赞表
    """

    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserInfo', null=True, on_delete=models.CASCADE)
    article = models.ForeignKey("Article", null=True, on_delete=models.CASCADE)
    is_up = models.BooleanField(default=True)

    class Meta:
        unique_together = [
            ('article', 'user'),
        ]


class Comment(models.Model):
    """

    评论表

    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid', on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    parent_comment = models.ForeignKey('self', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.content


# 日志表
class Log(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.CharField(max_length=64, verbose_name='访问IP', help_text='访问用户的IP地址')
    time = models.DateTimeField(auto_now_add=True, verbose_name='访问时间', help_text='该用户的访问时刻')
    url = models.CharField(max_length=64, verbose_name='访问的URL', help_text='该用户访问的URL地址')
    device = models.CharField(max_length=256, null=True, verbose_name='访问的浏览器', help_text='该用户是用什么浏览器访问的')
    platform = models.CharField(max_length=256, null=True, verbose_name='访问的系统', help_text='该用户用的是什么操作系统')

    # 定义这个表中默认显示的字段
    def __str__(self):
        return self.ip

    # 定义这个表在admin后台中显示的别名
    class Meta:
        ordering = ['id']
        verbose_name_plural = '日志'

# 轮播图表
class Swiper(models.Model):
    image = models.FileField(upload_to='swiper_img/', default='swiper_img/default.jpg', verbose_name='图片',
                             help_text='轮播图的图片')
    title = models.CharField(max_length=32, verbose_name='标题', help_text='图片的标题')
    img_url = models.CharField(max_length=64, verbose_name='URL', help_text='点击图片要跳转的URL地址')

    def __str__(self):
        return self.img_url

    class Meta:
        verbose_name_plural = '轮播图'