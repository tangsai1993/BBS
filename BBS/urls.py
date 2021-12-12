"""BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from app01 import views
from django.views.static import serve
from BBS import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/',views.register,name='reg'),
    url(r'^login/',views.login,name='login'),
    # 图片验证码相关操作
    url(r'^get_code/',views.get_code,name='gc'),
    url(r'^home/',views.home,name='home'),
    # 修改密码
    url(r'^set_password/',views.set_password,name='set_pwd'),
    # 退出登陆
    url(r'^logout/',views.logout,name='logout'),
    # 暴露后端指定文件夹资源
    url(r'^media/(?P<path>.*)',serve,{'document_root':settings.MEDIA_ROOT}),
    #点赞点踩
    url(r'up_or_down',views.up_or_down),
    #评论
    url(r'comment',views.comment),

    # 后台管理
    url(r'^backend/',views.backend),
    # 添加文章
    url(r'^add/article/',views.add_article),
    # 编辑器上传图片接口
    url(r'^upload_image/',views.upload_image),
    # 修改用户头像
    url(r'^set/avatar/',views.set_avatar),
    #日志路径
    url(r'^log/',views.log, name='log'),
    #个人信息页面
    url(r'^userinfo/',views.userinfo),
    #启用账户路由
    path('able_account/', views.able_account, name='able_account'),
    #禁用账户路由
    path('disable_account/', views.disable_account, name='disable_account'),
    #升级管理员路由
    path('super_account/',views.super_account,name='super_account'),
    #轮播图功能
    path('upload_swiper/', views.upload_swiper, name='upload_swiper'),

    # 个人站点页面搭建
    url(r'^(?P<username>\w+)/$',views.site,name='site'),
    # 侧边栏筛选功能
    # url(r'^(?P<username>\w+)/category/(\d+)/',views.site),
    # url(r'^(?P<username>\w+)/tag/(\d+)/',views.site),
    # url(r'^(?P<username>\w+)/archive/(\w+)/',views.site),
    # 上面的三条url其实可以合并成一条
    url(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/',views.site),
    # 文章详情页
    url(r'^(?P<username>\w+)/article/(?P<article_id>\d+)/',views.article_detail)
    ]