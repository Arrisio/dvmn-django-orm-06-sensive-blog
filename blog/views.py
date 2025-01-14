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
        "posts_with_tag": tag.posts__count,
    }


def index(request):
    most_popular_posts = (
        Post.objects.popular()[:5]
        .fetch_with_comments_count()
        .fetch_with_tags()
        .prefetch_related("author")
    )

    most_fresh_posts = (
        Post.objects.order_by("-published_at")
        .fetch_with_comments_count()
        .fetch_with_tags()
        .prefetch_related("author")
    )
    most_popular_tags = Tag.objects.popular()[:5].annotate(Count("posts"))

    context = {
        "most_popular_posts": [
            serialize_post(post) for post in most_popular_posts
        ],
        "page_posts": [serialize_post(post) for post in most_fresh_posts],
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, "index.html", context)


def post_detail(request, slug):
    post = (
        Post.objects
        .prefetch_related("comments", "comments__author", "author")
        .fetch_with_tags()
        .annotate(Count("likes"))
        .get_object_or_404(slug=slug)
    )

    serialized_comments = [
        {
            "text": comment.text,
            "published_at": comment.published_at,
            "author": comment.author.username,
        }
        for comment in post.comments.all()
    ]

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        "likes_amount": post.likes__count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
    }

    most_popular_tags = Tag.objects.popular()[:5].annotate(Count("posts"))

    most_popular_posts = (
        Post.objects.popular()[:5]
        .fetch_with_comments_count()
        .fetch_with_tags()
        .prefetch_related("author")
    )

    context = {
        "post": serialized_post,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "most_popular_posts": [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, "post-details.html", context)


def tag_filter(request, tag_title):
    most_popular_tags = Tag.objects.popular()[:5].annotate(Count("posts"))

    tag = Tag.objects.get_object_or_404(title=tag_title)
    related_posts = (
        tag.posts.all()[:20]
        .fetch_with_comments_count()
        .fetch_with_tags()
        .prefetch_related("author")
    )

    most_popular_posts = (
        Post.objects.popular()[:5]
        .fetch_with_comments_count()
        .fetch_with_tags()
        .prefetch_related("author")
    )

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
    return render(request, "contacts.html", {})
