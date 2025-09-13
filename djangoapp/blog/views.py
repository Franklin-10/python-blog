from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from blog.models import Post, Page
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.views.generic import ListView, DetailView

PER_PAGE = 9    

class PostListView(ListView):
    model = Post
    template_name = 'blog/pages/index.html'
    context_object_name = 'posts'
    ordering = '-pk',
    paginate_by = PER_PAGE
    queryset = Post.objects.get_published()

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     queryset = queryset.filter(is_published=True)
    #     return queryset
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Home'
        })
        return context

# def index(request):
#     posts = Post.objects.get_published()
#     paginator = Paginator(posts, PER_PAGE)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     return render(
#         request,
#        'blog/pages/index.html',
#        {
#            'page_obj': page_obj,
#            'page_title': 'Home',
#        }
#     )


class CreatedByListView(PostListView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._temp_context: dict[str, Any] = {}
        
    def get_context_data(self, **kwargs):
        ctx =  super().get_context_data(**kwargs)
        author_pk = self.kwargs.get('author_pk')
        user = self._temp_context['user']
        user_fullname = user.username

        if user.first_name:
            user_full_name = f'{user.first_name} {user.last_name}'
        page_title = user_full_name

        ctx.update({
            'page_title': page_title
        })
        return ctx
    
    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        queryset = queryset.filter(created_by__pk=self.kwargs.get('author_pk'))
        return queryset
    
    def get(self, request, *args, **kwargs) -> HttpResponse:
        author_pk = self.kwargs.get('author_pk')
        user = User.objects.filter(pk=author_pk).first()
        if user is None:
            raise Http404
        
        self._temp_context.update({
            'author_pk': author_pk,
            'user': user,
         })
        return super().get(request, *args, **kwargs)


class CategoryListView(PostListView):
    allow_empty = False

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(category__slug=self.kwargs.get('slug'))
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page_title = f'Categoria - {self.object_list[0].category.name}'    
        ctx.update({
            'page_title': page_title
        })
        return ctx
    

class TagListView(PostListView):
    allow_empty = False

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(tags__slug=self.kwargs.get('slug'))
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page_title = f'Tag - {self.object_list[0].tags.get(slug=self.kwargs.get("slug")).name}'  
        ctx.update({
            'page_title': page_title
        })
        return ctx
    
class SearchListView(PostListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._search_value = ''

    def setup(self, request, *args, **kwargs):
        self._search_value = request.GET.get('search', '').strip()
        return super().setup(request, *args, **kwargs)
    
    def get_queryset(self) -> QuerySet[Any]:
        search_value = self._search_value
        return super().get_queryset().filter(
            Q(title__icontains= search_value) |             
            Q(excerpt__icontains=search_value) |           
            Q(content__icontains=search_value)                   
        )[:PER_PAGE]    
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        search_value = self._search_value
        ctx.update({
            'page_title': f'{search_value[:30]} - Search',
            'search_value': search_value,

        })
        return ctx
    

    def get(self, request, *args, **kwargs):
        if self._search_value == '':
            return redirect('blog:index')
        return super().get(request, *args, **kwargs)

def search(request):
    search_value = request.GET.get('search', '').strip()
    posts = (
        Post.objects.get_published()
        .filter(
            Q(title__icontains=search_value) |           
            Q(excerpt__icontains=search_value) |           
            Q(content__icontains=search_value)                   
            )[:PER_PAGE]
    )
    
    page_title = f'{search_value[:30]} - Search'

    return render(
        request,
       'blog/pages/index.html',
       {
           'page_obj': posts,
           'search_value': search_value,
           'page_title': page_title,
       }
    )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/pages/post.html'
    slug_field = 'slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        post = self.get_object()
        page_title = f'{post.title}'
        ctx.update({
            'page_title': page_title
        })
        return ctx
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(is_published=True)
    

class PageDetailView(DetailView):
    model = Page
    template_name = 'blog/pages/page.html'
    slug_field = 'slug'
    context_object_name = 'page'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        page = self.get_object()
        page_title = f'{page.title}'
        ctx.update({
            'page_title': page_title
        })
        return ctx
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(is_published=True)



# Create your views here.
