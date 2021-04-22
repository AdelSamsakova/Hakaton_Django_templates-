from django.contrib import admin
from blog.models import Post, Comment, PostImage


class PostImageInLine(admin.TabularInline):
    model = PostImage
    fields = ['image', ]


class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageInLine, ]
    list_display = ['id', 'author', 'content']
    list_display_links = ['id', 'content']


admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
