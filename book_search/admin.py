from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.TopBBCBooks)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'picture',)
    search_fields = ('name',)


@admin.register(models.Genres)
class GenresAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)


@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'genre_id', 'image',)
    search_fields = ('name', 'genre', 'author',)
    list_filter = ('genre_id__name', 'author')


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'book_id', 'bbc_book_id', 'top_book_id', 'author_id')
    list_filter = ('active', 'created_at',)
    search_fields = ('book_id', 'bbc_book_id', 'author_id')


@admin.register(models.Top)
class TopAdmin(admin.ModelAdmin):
    list_display = ('name', 'top_type', 'author_id',)
    list_filter = ('top_type', 'author_id',)


@admin.register(models.TopType)
class TopTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.BookInTop)
class BookInTopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'image',)
    list_filter = ('author',)


@admin.register(models.Marketplace)
class MarketplaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'picture')


@admin.register(models.Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('value', 'user_id', 'book_id', 'top_book_id', 'bbc_book_id')


@admin.register(models.VoteStar)
class VoteStarAdmin(admin.ModelAdmin):
    list_display = ('value',)


@admin.register(models.Read)
class ReadAdmin(admin.ModelAdmin):
    list_display = ('is_read', 'user_id', 'book_id', 'top_book_id', 'bbc_book_id')


@admin.register(models.WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'book_id', 'top_book_id', 'bbc_book_id')
