---
name: "django-drf"
description: "When the user wants to build REST API endpoints using Django REST Framework. Use when the user says \"DRF,\" \"REST API,\" \"API endpoint,\" \"serializer,\" \"ViewSet,\" \"router,\" \"ModelSerializer,\" \"API authentication,\" \"JWT,\" \"Token auth,\" \"API permissions,\" \"pagination,\" \"filtering,\" \"throttling,\" \"nested serializer,\" or \"browsable API.\" For standard Django views without DRF, see django-views. For authentication setup, see django-auth."
---

# Django REST Framework

You are a DRF expert. Your goal is to help build clean, secure, and well-structured REST APIs.

## Initial Assessment

**Check for project context first:**
If `.agents/django-project-context.md` exists, read it to understand the API framework in use, authentication method (JWT, Token, Session), and existing API patterns.

Before writing code, identify:
1. **Resource**: What model/data is being exposed?
2. **Actions**: Which HTTP methods are needed (GET, POST, PUT, PATCH, DELETE)?
3. **Auth requirement**: Public, authenticated, or permission-based?

---

## Serializers

### ModelSerializer (Standard Pattern)

```python
from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'status', 'author', 'author_name', 'created_at']
        read_only_fields = ['author', 'created_at']

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError('Title must be at least 5 characters.')
        return value

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
```

### Nested Serializers

```python
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at']


class ArticleDetailSerializer(ArticleSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(ArticleSerializer.Meta):
        fields = ArticleSerializer.Meta.fields + ['comments']
```

### Read vs Write Serializers

For complex APIs, use separate serializers:

```python
class ArticleReadSerializer(serializers.ModelSerializer):
    author = UserSummarySerializer(read_only=True)
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'created_at']

class ArticleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'content', 'status']
```

---

## ViewSets

### ModelViewSet (Full CRUD)

```python
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user).select_related('author')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ArticleReadSerializer
        return ArticleWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        article = self.get_object()
        article.status = Article.Status.PUBLISHED
        article.save()
        return Response({'status': 'published'})
```

### Restricted ViewSets

```python
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

class ArticleReadOnlyViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """Read-only: only list and retrieve."""
    queryset = Article.objects.published()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]
```

---

## Routers & URL Configuration

```python
# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('articles', views.ArticleViewSet, basename='article')
router.register('users', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
```

**Router generates:**
| URL | Method | Action |
|-----|--------|--------|
| `/articles/` | GET | list |
| `/articles/` | POST | create |
| `/articles/{pk}/` | GET | retrieve |
| `/articles/{pk}/` | PUT | update |
| `/articles/{pk}/` | PATCH | partial_update |
| `/articles/{pk}/` | DELETE | destroy |
| `/articles/{pk}/publish/` | POST | publish (custom) |

---

## Authentication

### JWT (Recommended — simplejwt)

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# urls.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns += [
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
]
```

### Token Auth (Simple)

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
```

---

## Permissions

```python
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
```

**Built-in permissions:**
| Class | Behavior |
|-------|---------|
| `AllowAny` | No auth required |
| `IsAuthenticated` | Must be logged in |
| `IsAdminUser` | Must be `is_staff=True` |
| `IsAuthenticatedOrReadOnly` | Auth for writes, public reads |

---

## Filtering, Search & Ordering

```python
# pip install django-filter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class ArticleViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'author']           # ?status=published&author=1
    search_fields = ['title', 'content']              # ?search=django
    ordering_fields = ['created_at', 'title']         # ?ordering=-created_at
    ordering = ['-created_at']                        # Default ordering
```

---

## Pagination

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Custom pagination
from rest_framework.pagination import PageNumberPagination

class SmallPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
```

---

## Error Handling

```python
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

def get_article(pk, user):
    try:
        article = Article.objects.get(pk=pk)
    except Article.DoesNotExist:
        raise NotFound('Article not found.')
    if article.author != user:
        raise PermissionDenied('You do not own this article.')
    return article
```

---

## Settings Summary

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Browsable API
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
```

---

## Related Skills

- **django-models**: The models being serialized and queried
- **django-auth**: Authentication setup and custom user model
- **django-performance**: select_related/prefetch_related in get_queryset()
- **django-tests**: Testing API endpoints with APIClient
