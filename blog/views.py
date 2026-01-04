from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.conf import settings

from .models import Post
from .forms import EmailPostForm


class PostListView(ListView):
    """Альтернативное представление списка постов"""
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request: HttpRequest):
    all_posts = Post.published.all()
    paginator = Paginator(all_posts, 3)
    page_num = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_num)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, "blog/post/list.html", {"posts": posts})


def post_detail(request: HttpRequest, year: int, month: int, day: int, slug: str):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=slug,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    return render(request, "blog/post/detail.html", {"post": post})

def post_share(request, post_id):
    # извлекаем пост по id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == "POST":
        # Форма была передана на обработку
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля формы успешно прошли валидацию
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}'s ({cd['email']}) comments: {cd['comments']}"
            to = cd['to']
            if isinstance(to, str):
                if ',' not in to:
                    to = [to]
                else:
                    to = [to_s.strip() for to_s in to.split(',')]
            send_mail(subject, message, settings.EMAIL_HOST_USER, to)
            sent = True
    else:
        form = EmailPostForm()
    return render(request, "blog/post/share.html", {"post": post, "form": form, 'sent': sent})