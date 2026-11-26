from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.utils import add_xp, get_profile
from dashboard.utils import log_activity

from .forms import CommentForm, PostForm
from .models import Comment, Post


def verified_required(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if not get_profile(request.user).email_verified:
            messages.warning(request, 'Please verify your email address before posting. Check your inbox or resend the link.')
            return redirect('community:list')
        return view(request, *args, **kwargs)
    return login_required(inner)


def post_list(request):
    qs = Post.objects.select_related('author', 'shared_reaction').annotate(n_comments=Count('comments', distinct=True),
                                                                         n_likes=Count('likes', distinct=True))
    cat, q, sort = request.GET.get('category', ''), request.GET.get('q', '').strip(), request.GET.get('sort', 'new')
    if cat:
        qs = qs.filter(category=cat)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q))
    if sort == 'top':
        qs = qs.order_by('-n_likes', '-created_at')
    elif sort == 'active':
        qs = qs.order_by('-n_comments', '-created_at')
    page = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'community/list.html', {'page': page, 'cat': cat, 'q': q, 'sort': sort,
                                                   'categories': Post._meta.get_field('category').choices})


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author', 'shared_reaction'), pk=pk)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next={request.path}")
        if not get_profile(request.user).email_verified:
            messages.warning(request, 'Verify your email address to reply.')
            return redirect('community:detail', pk=pk)
        if form.is_valid():
            c = form.save(commit=False)
            c.post, c.author = post, request.user
            c.save()
            add_xp(request.user, 3)
            messages.success(request, 'Reply posted.')
            return redirect(f'{request.path}#c{c.pk}')
    liked = request.user.is_authenticated and post.likes.filter(pk=request.user.pk).exists()
    return render(request, 'community/detail.html', {'post': post, 'form': form, 'liked': liked,
                                                     'comments': post.comments.select_related('author')})


@verified_required
def create(request, pk=None):
    inst = get_object_or_404(Post, pk=pk, author=request.user) if pk else None
    initial = {}
    if not inst and request.GET.get('reaction', '').isdigit():
        initial = {'shared_reaction': request.GET['reaction'], 'category': 'reaction'}
    form = PostForm(request.POST or None, instance=inst, user=request.user, initial=initial)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        if not inst:
            add_xp(request.user, 10)
            log_activity(request.user, 'post', f'Posted “{post.title}”', f'/community/{post.pk}/')
        messages.success(request, 'Post saved.')
        return redirect('community:detail', pk=post.pk)
    return render(request, 'community/form.html', {'form': form, 'editing': inst})


@login_required
@require_POST
def like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('community:detail', pk=pk)


@login_required
@require_POST
def delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('community:detail', pk=pk)
    post.delete()
    messages.info(request, 'Post deleted.')
    return redirect('community:list')


@login_required
@require_POST
def delete_comment(request, pk):
    c = get_object_or_404(Comment, pk=pk)
    if c.author == request.user or request.user.is_staff:
        c.delete()
        messages.info(request, 'Reply deleted.')
    return redirect('community:detail', pk=c.post_id)
