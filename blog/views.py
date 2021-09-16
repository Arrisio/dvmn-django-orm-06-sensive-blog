from django.db.models import Count, Value, IntegerField
from django.shortcuts import render
from blog.models import Comment, Post, Tag


def get_related_posts_count(tag):
    return tag.posts.count()


def serialize_post(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": len(Comment.objects.filter(post=post)),
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
        "first_tag_title": post.tags.all()[0].title,
    }


def serialize_post_optimized(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments__count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
        "first_tag_title": post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        "title": tag.title,
        "posts_with_tag": len(Post.objects.filter(tags=tag)),
        # "posts_with_tag": tag.posts__count,
    }


def index(request):
    most_popular_posts = (
        Post.objects.all()
        .annotate(Count("likes"))
        .order_by("-likes__count")
    )[:5].fetch_with_comments_count().prefetch_related("author")

    # posts_with_comments = {
    #     post.id: post.comments__count
    #     for post in Post.objects.filter(
    #         id__in=[post.id for post in most_popular_posts]
    #     ).annotate(Count("comments"))
    # }
    posts_with_comments = most_popular_posts
    # for post in most_popular_posts:
    #     post.comments__count = posts_with_comments[post.id]

    most_fresh_posts = (
        Post.objects.order_by("-published_at")
        .prefetch_related("author")
        .annotate(Count("comments", distinct=True))[:5]
    )

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        "most_popular_posts": [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
        "page_posts": [
            serialize_post_optimized(post) for post in most_fresh_posts
        ],
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, "index.html", context)


def post_detail(request, slug):
    post = Post.objects.get(slug=slug)
    comments = Comment.objects.filter(post=post)
    serialized_comments = []
    for comment in comments:
        serialized_comments.append(
            {
                "text": comment.text,
                "published_at": comment.published_at,
                "author": comment.author.username,
            }
        )

    likes = post.likes.all()

    related_tags = post.tags.all()

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        "likes_amount": len(likes),
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = []  # TODO. Как это посчитать?

    context = {
        "post": serialized_post,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "most_popular_posts": [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, "post-details.html", context)


def tag_filter(request, tag_title):
    most_popular_tags = Tag.objects.popular()[:5]

    tag = Tag.objects.get(title=tag_title)
    related_posts = tag.posts.prefetch_related("author").all()[:20]

    most_popular_posts = []  # TODO. Как это посчитать?

    context = {
        "tag": tag.title,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "posts": [serialize_post(post) for post in related_posts],
        "most_popular_posts": [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, "posts-list.html", context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, "contacts.html", {})
