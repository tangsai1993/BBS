from django.shortcuts import render, HttpResponse, redirect
from app01.myforms import MyRegForm
from app01 import models
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
import random
from django.contrib import auth


# Create your views here.


def register(request):
    form_obj = MyRegForm()
    if request.method == 'POST':
        back_dic = {"code": 1000, 'msg': ''}
        # 校验数据是否合法
        form_obj = MyRegForm(request.POST)
        # 判断数据是否合法
        if form_obj.is_valid():
            # print(form_obj.cleaned_data)  # {'username': 'jason', 'password': '123', 'confirm_password': '123', 'email': '123@qq.com'}
            clean_data = form_obj.cleaned_data  # 将校验通过的数据字典赋值给一个变量
            # 将字典里面的confirm_password键值对删除
            clean_data.pop('confirm_password')  # {'username': 'jason', 'password': '123', 'email': '123@qq.com'}
            # 用户头像
            file_obj = request.FILES.get('avatar')
            """针对用户头像一定要判断是否传值 不能直接添加到字典里面去"""
            if file_obj:
                clean_data['avatar'] = file_obj
            # 直接操作数据库保存数据
            models.UserInfo.objects.create_user(**clean_data)
            back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)
    return render(request, 'register.html', locals())


def login(request):
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # 1 先校验验证码是否正确      自己决定是否忽略            统一转大写或者小写再比较
        if request.session.get('code').upper() == code.upper():
            # 2 校验用户名和密码是否正确
            user_obj = auth.authenticate(request, username=username, password=password)
            if user_obj:
                # 保存用户状态
                auth.login(request, user_obj)
                back_dic['url'] = '/home/'
            else:
                back_dic['code'] = 2000
                back_dic['msg'] = '用户名或密码错误'
        else:
            back_dic['code'] = 3000
            back_dic['msg'] = '验证码错误'
        return JsonResponse(back_dic)
    return render(request, 'login.html')


"""
图片相关的模块
    pip3 install pillow
"""
from PIL import Image, ImageDraw, ImageFont

"""
Image:生成图片
ImageDraw:能够在图片上乱涂乱画
ImageFont:控制字体样式
"""
from io import BytesIO, StringIO

"""
内存管理器模块
BytesIO:临时帮你存储数据 返回的时候数据是二进制
StringIO:临时帮你存储数据 返回的时候数据是字符串
"""


def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_code(request):
    # 推导步骤1:直接获取后端现成的图片二进制数据发送给前端
    # with open(r'static/img/111.jpg','rb') as f:
    #     data = f.read()
    # return HttpResponse(data)

    # 推导步骤2:利用pillow模块动态产生图片
    # img_obj = Image.new('RGB',(430,35),'green')
    # img_obj = Image.new('RGB',(430,35),get_random())
    # # 先将图片对象保存起来
    # with open('xxx.png','wb') as f:
    #     img_obj.save(f,'png')
    # # 再将图片对象读取出来
    # with open('xxx.png','rb') as f:
    #     data = f.read()
    # return HttpResponse(data)

    # 推导步骤3:文件存储繁琐IO操作效率低  借助于内存管理器模块
    # img_obj = Image.new('RGB', (430, 35), get_random())
    # io_obj = BytesIO()  # 生成一个内存管理器对象  你可以看成是文件句柄
    # img_obj.save(io_obj,'png')
    # return HttpResponse(io_obj.getvalue())  # 从内存管理器中读取二进制的图片数据返回给前端

    # 最终步骤4:写图片验证码
    img_obj = Image.new('RGB', (430, 35), get_random())
    img_draw = ImageDraw.Draw(img_obj)  # 产生一个画笔对象
    img_font = ImageFont.truetype('static/font/222.ttf', 30)  # 字体样式 大小

    # 随机验证码  五位数的随机验证码  数字 小写字母 大写字母
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        # 从上面三个里面随机选择一个
        tmp = random.choice([random_lower, random_upper, random_int])
        # 将产生的随机字符串写入到图片上
        """
        为什么一个个写而不是生成好了之后再写
        因为一个个写能够控制每个字体的间隙 而生成好之后再写的话
        间隙就没法控制了
        """
        img_draw.text((i * 60 + 60, -2), tmp, get_random(), img_font)
        # 拼接随机字符串
        code += tmp
    print(code)
    # 随机验证码在登陆的视图函数里面需要用到 要比对 所以要找地方存起来并且其他视图函数也能拿到
    request.session['code'] = code
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


def home(request):
    article_list = models.Article.objects.all()
    return render(request, 'home.html', locals())


from django.contrib.auth.decorators import login_required


@login_required
def set_password(request):
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            is_right = request.user.check_password(old_password)
            if is_right:
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    back_dic['msg'] = '修改成功'
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '两次密码不一致'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '原密码错误'
        return JsonResponse(back_dic)


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/home/')


def site(request, username, **kwargs):
    """
    :param request:
    :param username:
    :param kwargs: 如果该参数有值 也就意味着需要对article_list做额外的筛选操作
    :return:
    """
    # 先校验当前用户名对应的个人站点是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 用户如果不存在应该返回一个404页面
    if not user_obj:
        return render(request, 'errors.html')
    blog = user_obj.blog
    # 查询当前个人站点下的所有的文章
    article_list = models.Article.objects.filter(user__username=username)  # queryset对象 侧边栏的筛选其实就是对article_list再进一步筛选
    if kwargs:
        # print(kwargs)  # {'condition': 'tag', 'param': '1'}
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        # 判断用户到底想按照哪个条件筛选数据
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__nid=param)
        else:
            year, month = param.split('-')  # 2020-11  [2020,11]
            article_list = article_list.filter(create_time__year=year, create_time__month=month)

    # # 1 查询当前用户所有的分类及分类下的文章数
    # category_list = models.Category.objects.filter(blog__userinfo__username=username).annotate(count_num=Count('article__pk')).values_list('title','count_num','pk')
    # # print(category_list)  # <QuerySet [('jason的分类一', 2), ('jason的分类二', 1), ('jason的分类三', 1)]>
    #
    # # 2 查询当前用户所有的标签及标签下的文章数
    # tag_list = models.Tag.objects.filter(blog__userinfo__username=username).annotate(count_num=Count('article__pk')).values_list('title','count_num','pk')
    # # print(tag_list)  # <QuerySet [('tank的标签一', 1), ('tank的标签二', 1), ('tank的标签三', 2)]>
    #
    # # 3 按照年月统计所有的文章
    # date_list = models.Article.objects.filter(user__username=username).annotate(month=TruncMonth('create_time')).values('month').annotate(count_num=Count('pk')).values_list('month','count_num')
    # # print(date_list)

    return render(request, 'site.html', locals())


def article_detail(request, username, article_id):
    """
   应该需要校验username和article_id是否存在,但是我们这里先只完成正确的情况
   默认不会瞎搞
   :param request:
   :param username:
   :param article_id:
   :return:
   """
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 先获取文章对象
    article_obj = models.Article.objects.filter(pk=article_id, user__username=username).first()
    if not article_obj:
        return render(request, 'errors.html')
    # 获取当前 文章所有的评论内容
    comment_list = models.Comment.objects.filter(article=article_obj)
    return render(request, 'article_detail.html', locals())


import json
from django.db.models import F


def up_or_down(request):
    """
    1.校验用户是否登陆
    2.判断当前文章是否是当前用户自己写的(自己不能点自己的文章)
    3.当前用户是否已经给当前文章点过了
    4.操作数据库了
    :param request:
    :return:
    """
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        # 1 先判断当前用户是否登陆
        if request.user.is_authenticated:
            article_id = request.POST.get('article_id')
            is_up = request.POST.get('is_up')
            # print(is_up,type(is_up))  # true <class 'str'>
            is_up = json.loads(is_up)  # 记得转换
            # print(is_up, type(is_up))  # True <class 'bool'>
            # 2 判断当前文章是否是当前用户自己写的  根据文章id查询文章对象 根据文章对象查作者 根request.user比对
            article_obj = models.Article.objects.filter(pk=article_id).first()
            if not article_obj.user == request.user:
                # 3 校验当前用户是否已经点了      哪个地方记录了用户到底点没点
                is_click = models.ArticleUpDown.objects.filter(user=request.user, article=article_obj)
                if not is_click:
                    # 4 操作数据库 记录数据      要同步操作普通字段
                    # 判断当前用户点了赞还是踩 从而决定给哪个字段加一
                    if is_up:
                        # 给点赞数加一
                        models.Article.objects.filter(pk=article_id).update(up_count=F('up_count') + 1)
                        back_dic['msg'] = '点赞成功'
                    else:
                        # 给点踩数加一
                        models.Article.objects.filter(pk=article_id).update(down_count=F('down_count') + 1)
                        back_dic['msg'] = '点踩成功'
                    # 操作点赞点踩表
                    models.ArticleUpDown.objects.create(user=request.user, article=article_obj, is_up=is_up)
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '你已经点过了,不能再点了'  # 这里你可以做的更加的详细 提示用户到底点了赞还是点了踩
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '你个臭不要脸的!'
        else:
            back_dic['code'] = 1003
            back_dic['msg'] = '请先<a href="/login/">登陆</a>'
        return JsonResponse(back_dic)


from django.db import transaction


def comment(request):
    # 自己也可以给自己的文章评论内容
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ""}
        if request.method == 'POST':
            if request.user.is_authenticated:
                article_id = request.POST.get('article_id')
                content = request.POST.get("content")
                parent_id = request.POST.get('parent_id')
                # 直接操作评论表 存储数据      两张表
                with transaction.atomic():
                    models.Article.objects.filter(pk=article_id).update(comment_count=F('comment_count') + 1)
                    models.Comment.objects.create(user=request.user, article_id=article_id, content=content,
                                                  parent_comment_id=parent_id)
                back_dic['msg'] = '评论成功'
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = '用户未登陆'
            return JsonResponse(back_dic)


from app01.utils.mypage import Pagination


@login_required
def backend(request):
    # 获取当前用户对象所有的文章展示到页面
    article_list = models.Article.objects.filter(user=request.user)

    page_obj = Pagination(current_page=request.GET.get('page', 1), all_count=article_list.count())
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request, 'backend/backend.html', locals())


from bs4 import BeautifulSoup


@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get("category")
        tag_id_list = request.POST.getlist('tag')
        # 模块使用
        soup = BeautifulSoup(content, 'html.parser')

        tags = soup.find_all()
        # 获取所有的标签
        for tag in tags:
            # print(tag.name)  # 获取页面所有的标签
            # 针对script标签 直接删除
            if tag.name == 'script':
                # 删除标签
                tag.decompose()
        # 文章简介
        # 1 先简单暴力的直接切去content 150个字符
        # desc = content[0:150]
        # 2 截取文本150个
        desc = soup.text[0:150]
        article_obj = models.Article.objects.create(
            title=title,
            content=str(soup),
            desc=desc,
            category_id=category_id,
            user=request.user
        )
        # 文章和标签的关系表 是我们自己创建的 没法使用add set remove clear方法
        # 自己去操作关系表   一次性可能需要创建多条数据      批量插入bulk_create()
        article_obj_list = []
        for i in tag_id_list:
            tag_article_obj = models.Article2Tag(article=article_obj, tag_id=i)
            article_obj_list.append(tag_article_obj)
        # 批量插入数据
        models.Article2Tag.objects.bulk_create(article_obj_list)
        # 跳转到后台管理文章展示页
        return redirect('/backend/')
    category_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)
    # print(request.user.blog)
    # print(category_list,tag_list)
    return render(request, 'backend/add_article.html', locals())


import os
from BBS import settings


def upload_image(request):
    """
         //成功时
        {
                "error" : 0,
                "url" : "http://www.example.com/path/to/file.ext"
        }
        //失败时
        {
                "error" : 1,
                "message" : "错误信息"
        }
    :param request:
    :return:
    """
    back_dic = {'error': 0, }  # 先提前定义返回给编辑器的数据格式

    # 用户写文章上传的图片 也算静态资源 也应该防盗media文件夹下

    if request.method == "POST":
        # 获取用户上传的图片对象
        # print(request.FILES)  # 打印看到了健固定叫imgFile
        file_obj = request.FILES.get('imgFile')
        # 手动拼接存储文件的路径
        file_dir = os.path.join(settings.BASE_DIR, 'media', 'article_img')
        # 优化操作 先判断当前文件夹是否存在 不存在 自动创建
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)  # 创建一层目录结构  article_img
        # 拼接图片的完整路径
        file_path = os.path.join(file_dir, file_obj.name)
        with open(file_path, 'wb') as f:
            for line in file_obj:
                f.write(line)
        back_dic['url'] = '/media/article_img/%s' % file_obj.name

    return JsonResponse(back_dic)


@login_required
def set_avatar(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar')
        # models.UserInfo.objects.filter(pk=request.user.pk).update(avatar=file_obj)  # 不会再自动加avatar前缀
        # 1.自己手动加前缀
        # 2.换一种更新方式
        user_obj = request.user
        user_obj.avatar = file_obj
        user_obj.save()
        return redirect('/home/')
    blog = request.user.blog
    username = request.user.username
    return render(request, 'set_avatar.html', locals())


from django.core.paginator import Paginator


def log(request):
    log_num = models.Log.objects.count()
    page_num_int = int(request.GET.get('page', 1))
    log_list = models.Log.objects.all()
    paginator = Paginator(log_list, 10)
    if paginator.num_pages > 9:
        if page_num_int - 4 < 1:
            page_range = range(1, 9)
        elif page_num_int + 4 > paginator.num_pages:
            page_range = range(paginator.num_pages - 8, paginator.num_pages + 1)
        else:
            page_range = range(page_num_int - 4, page_num_int + 4)
    else:
        page_range = paginator.page_range
    page = paginator.page(page_num_int)
    return render(request, 'other/log.html', locals())


def userinfo(request):
    '''
    个人信息页面函数
    :param request:
    :return:
    '''
    info = models.UserInfo.objects.all()

    return render(request, 'other/userinfo.html', locals())


def able_account(request):
    '''
    激活用户视图函数
    :param request:
    :return:
    '''
    able_id = request.GET.get('able_id')
    models.UserInfo.objects.filter(nid=able_id).update(is_active=1)
    return redirect('/userinfo/')


def disable_account(request):
    '''
    禁用用户视图
    :param request:
    :return:
    '''
    disable_id = request.GET.get('disable_id')
    models.UserInfo.objects.filter(nid=disable_id).update(is_active=0)
    return redirect('/userinfo/')


def super_account(request):
    '''
    提升管理员视图
    :param request:
    :return:
    '''

    return HttpResponse('ok')


def upload_swiper(request):
    '''
    轮播图功能视图
    :param request:
    :return:
    '''
    if request.method == 'POST':
        file = request.FILES.get('swiper_img')
        url = request.POST.get('url')
        title = request.POST.get('title')
        models.Swiper.objects.create(image=file, img_url=url, title=title)
        return redirect('upload_swiper')

    elif request.method == 'GET':
        swiper_list = models.Swiper.objects.all()
        return render(request, 'other/UploadSwiper.html', {'swiper_list': swiper_list})
