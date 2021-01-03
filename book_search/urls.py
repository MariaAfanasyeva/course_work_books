from django.urls import path
from . import views
from django.contrib import admin


urlpatterns = [
    path('', views.main_activity_view, name='main_activity'),
    path('genre/<genre>', views.books_per_genres, name='book_per_genres'),
    path('book/<book_id>/<is_bbc>', views.info_about_book, name='info_about_book'),
    path('book/comment/<book_id>/<is_bbc>/', views.add_comment, name='add_comment'),
    path('make_top/', views.make_top, name='make_top'),
    path('add_book_to_top/', views.add_book_into_top, name='add_book_top'),
    path('authors/', views.get_all_authors, name='authors'),
    path('topbbc/', views.get_top_bbc_books, name='top_bbc_books'),
    path('author/<author>', views.books_per_authors, name='books_author'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('book/share/<book_id>/<is_bbc>/', views.share_book, name='share_book'),
    path('all_tops/', views.show_tops, name='tops'),
    path('add_rating/<book_id>/<is_bbc>/', views.add_rating, name='add_rating'),
    path('read/<book_id>/<is_bbc>/', views.read, name='read'),
    path('person/', views.personal, name='person'),
    path('add_wishlist/<book_id>/<is_bbc>/', views.add_book_into_wishlist, name='wishlist'),
    path('delete_wishlist/<book_id>/<is_bbc>/', views.delete_book_from_wishlist, name='delete_wishlist'),
    path('search_litres/', views.add_book_with_litres, name='add_with_litres'),
    path('add_book/', views.add_book, name='add_book_manual'),
    path('wish_list/', views.wish_list, name='user_wishlist'),
    path('read_list/', views.read_list, name='read_list'),
]
