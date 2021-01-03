from django.core.files.base import ContentFile
from urllib.parse import urlparse
import difflib
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from . import models
import requests
from io import StringIO
from lxml import etree
from random import choice
from django.core.paginator import Paginator
from .forms import CommentForm, UserRegisterForm, UserLoginForm, ShareBookForm, MakeTopForm, AddBookIntoTop, \
    VotingForm, ReadForm, AddBook
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
# Create your views here.


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect('main_activity')
        else:
            messages.error(request, 'Произошла ошибка регистрации!')
    else:
        form = UserRegisterForm()
    return render(request, 'book_search/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main_activity')
    else:
        form = UserLoginForm()
    return render(request, 'book_search/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')


def main_activity_view(request):
    genres = models.Genres.objects.all()
    top_bbc_books = models.TopBBCBooks.objects.all()
    ten_bbc_books = []
    x = 0
    for i in range(10):
        book = choice(top_bbc_books)
        ten_bbc_books.append(book)
    return render(request, 'book_search/main.html', {'genres': genres, 'ten_bbc_books': ten_bbc_books})


def books_per_genres(request, genre):
    genres = models.Genres.objects.all()
    books = models.Book.objects.filter(genre_id__name=genre)
    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'book_search/books_genres.html', {'genres': genres, 'page_obj': page_obj, 'my_genre': genre})


def get_all_authors(request):
    genres = models.Genres.objects.all()
    books = models.Book.objects.all()
    authors = set()
    books_per_authors = dict()
    for book in books:
        authors.add(book.author)
    authors = sorted(list(authors))
    for author in authors:
        books = models.Book.objects.filter(author=author)
        books_per_authors[author] = books
    paginator = Paginator(authors, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'book_search/all_authors.html', {'page_obj': page_obj, 'genres': genres,
                                                            'books_per_authors': books_per_authors})


def get_top_bbc_books(request):
    books = models.TopBBCBooks.objects.all()
    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    genres = models.Genres.objects.all()
    return render(request, 'book_search/tob_bbc.html', {'page_obj': page_obj, 'genres': genres})


def info_about_book(request, book_id, is_bbc):
    if is_bbc == '1':
        try:
            in_list = models.WishList.objects.get(bbc_book_id=book_id, user_id=request.user)
        except Exception:
            in_list = None
    elif is_bbc == '0':
        try:
            in_list = models.WishList.objects.get(book_id=book_id, user_id=request.user)
        except Exception:
            in_list = None
    else:
        try:
            in_list = models.WishList.objects.get(top_book_id=book_id, user_id=request.user)
        except Exception:
            in_list = None

    rate_form = VotingForm()

    read_form = ReadForm()

    form = CommentForm()

    if is_bbc == '1':
        book = models.TopBBCBooks.objects.get(id=book_id)
    elif is_bbc == '0':
        book = models.Book.objects.get(id=book_id)
    else:
        book = models.BookInTop.objects.get(id=book_id)
    marketplaces = models.Marketplace.objects.all()
    genres = models.Genres.objects.all()
    book_name = book.name.replace(' ', '+')
    book_author = book.author.split(' ')
    book_author = book_author[-1]
    if is_bbc == '1':
        comments = models.Comment.objects.filter(bbc_book_id=book_id)
        if request.user.is_authenticated:
            try:
                mark = models.Vote.objects.get(bbc_book_id=book_id, user_id=request.user)
            except Exception:
                mark = None
            try:
                readd = models.Read.objects.get(bbc_book_id=book_id, user_id=request.user)
            except Exception:
                readd = None
        else:
            mark = None
            readd = None
    elif is_bbc == '0':
        comments = models.Comment.objects.filter(book_id=book_id)
        if request.user.is_authenticated:
            try:
                mark = models.Vote.objects.get(book_id=book_id, user_id=request.user)
            except Exception:
                mark = None
            try:
                readd = models.Read.objects.get(book_id=book_id, user_id=request.user)
            except Exception:
                readd =None
        else:
            mark = None
            readd = None
    else:
        comments = models.Comment.objects.filter(top_book_id=book_id)
        if request.user.is_authenticated:
            try:
                mark = models.Vote.objects.get(top_book_id=book_id, user_id=request.user)
            except Exception:
                mark = None
            try:
                readd = models.Read.objects.get(top_book_id=book_id, user_id=request.user)
            except Exception:
                readd = None
        else:
            mark = None
            readd = None

    """Flibusta parser"""
    root = 'https://flibusta.is/booksearch?ask=' + book_name
    response = requests.get(root)
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(str(response.text)), parser=parser)
    try:
        book_flib = tree.xpath('//div[@class="clear-block"]//ul//li//a/@href')
        flibusta_link = 'https://flibusta.is' + book_flib[-2]
    except Exception:
        flibusta_link = None

    """OZ.by parser"""
    root = 'https://oz.by/search/?c=1101523&q=' + book_name + '+' + book_author
    response = requests.get(root)
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(str(response.text)), parser=parser)
    l_list = tree.xpath('//a[@class="needsclick item-type-card__link item-type-card__link--main"]/@href')
    if not l_list:
        price_oz = 'Данной книги нет в наличии'
        link_oz = None
    else:
        l_list = l_list[0]
        link_oz = 'https://oz.by' + l_list
        new_response = requests.get(link_oz)
        tree = etree.parse(StringIO(str(new_response.text)), parser=parser)
        price = tree.xpath('//span[@class="b-product-control__text b-product-control__text_main"]/text()')# [0]
        if not price:
            price_oz = 'В данный момент книги нет в наличии'
        else:
            price = price[0]
            price_oz = price.replace('\xa0', ' ')

    """Wildberries parser"""
    book_name = book_name.replace('+', '%20')
    link_wildberries = 'https://by.wildberries.ru/catalog/0/search.aspx?subject=786&search=' + book_name + '%20' + book_author + '&sort=priceup'
    response = requests.get(link_wildberries)
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(str(response.text)), parser=parser)
    l_list = tree.xpath('//ins[@class="lower-price"]/text()')
    if not l_list:
        price_wildberries = 'Данной книги нет в наличии'
        link_wildberries = None
    else:
        price_wildberries = l_list[0]

    """Litres parser"""
    book_name = book_name.replace('\xa0', '%20')
    book_list = list(book_name)
    if is_bbc == '1':
        book_list.remove('«')
        book_list.remove('»')
    book_name = ''.join(book_list)
    root = 'https://www.litres.ru/pages/rmd_search/?q=' + book_name + '%20' + book_author
    response = requests.get(root)
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(str(response.text)), parser=parser)
    l_list = tree.xpath('//div[@class="art-item__name"]')
    if not l_list:
        price_litres = tree.xpath('//span[@class="biblio_book_buy__ru"]//span[@class="simple-price"]/text()')
        if not price_litres:
            price_litres = 'Данной книги нет в наличии'
            link_litres = None
        else:
            price_litres = str(price_litres[0]) + ' руб'
            link_litres = root
    else:
        l_list = l_list[0]
        book_href = l_list.xpath('.//a[@class="art-item__name__href"]/@href')
        link_litres = 'https://www.litres.ru' + book_href[0]
        response = requests.get(link_litres)
        tree = etree.parse(StringIO(str(response.text)), parser=parser)
        price_litres = tree.xpath('//span[@class="biblio_book_buy__ru"]//span[@class="simple-price"]/text()')
        if price_litres:
            price_litres = price_litres[0]
        else:
            price_litres = None
        price_litres = str(price_litres) + ' руб'
    links = dict()
    hrefs = [link_oz, link_wildberries, link_litres]
    prices = [price_oz, price_wildberries, price_litres]
    i = 0
    for marketplace in marketplaces:
        links[marketplace.name] = dict()
        links[marketplace.name]['link'] = hrefs[i]
        links[marketplace.name]['price'] = prices[i]
        i += 1
        links[marketplace.name]['query'] = marketplaces
    return render(request, 'book_search/book_info.html', {'book': book, 'genres': genres,
                                                          'comments': comments,
                                                          'is_bbc': is_bbc,
                                                          'marketplaces': marketplaces,
                                                          'links': links,
                                                          'form': form,
                                                          'rate_form': rate_form,
                                                          'mark': mark,
                                                          'read_form': read_form,
                                                          'readd': readd,
                                                          'in_list': in_list,
                                                          'flibusta_link': flibusta_link})


@login_required
def add_comment(request, book_id, is_bbc):
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author_id = request.user
            if is_bbc == '1':
                new_comment.bbc_book_id = models.TopBBCBooks.objects.get(id=book_id)
            elif is_bbc == '0':
                new_comment.book_id = models.Book.objects.get(id=book_id)
            else:
                new_comment.top_book_id = models.BookInTop.objects.get(id=book_id)
            new_comment.save()
            return redirect('info_about_book', book_id, is_bbc)
    else:
        form = CommentForm()
    return render(request, 'book_search/add_comment.html', {'form': form})


@login_required
def make_top(request):
    if request.method == 'POST':
        form = MakeTopForm(data=request.POST)
        if form.is_valid():
            new_top = form.save(commit=False)
            new_top.author_id = request.user
            new_top.save()
            form.save_m2m()
            return redirect('person')
    else:
        form = MakeTopForm()
    return render(request, 'book_search/make_top.html', {'form': form})


def add_book_into_top(request):
    if request.method == 'POST':
        form = AddBookIntoTop(request.POST, request.FILES)
        if form.is_valid():
            new_book = form.save(commit=False)
            new_book.save()
            return redirect('add_book')
    else:
        form = AddBookIntoTop()
    return render(request, 'book_search/add_book_top.html', {'form': form})


def books_per_authors(request, author):
    books = models.Book.objects.filter(author=author)
    all_books = set()
    for book in books:
        all_books.add(book.name)
    book_query = list()
    books_by = list()
    books_by_author = dict()
    for book in all_books:
        books = models.Book.objects.filter(name=book)
        for book_ in books:
            book_query.append(book_)
            break
    books_by.extend(book_query)
    for book in all_books:
        books = models.Book.objects.filter(name=book)
        genre_list = list()
        for book_ in books:
            genre_list.append(book_.genre_id.name)
        books_by_author[book] = dict()
        books_by_author[book]['genres'] = genre_list
        books_by_author[book]['query'] = books_by
    genres = models.Genres.objects.all()
    return render(request, 'book_search/books_author.html', {'books_by_author': books_by_author, 'genres': genres,
                                                             'author': author, 'all_books': all_books})


def share_book(request, book_id, is_bbc):
    if is_bbc == '1':
        book = get_object_or_404(models.TopBBCBooks, id=book_id)
    elif is_bbc == '0':
        book = get_object_or_404(models.Book, id=book_id)
    else:
        book = get_object_or_404(models.BookInTop, id=book_id)
    sent = False
    if request.method == 'POST':
        form = ShareBookForm(request.POST)
        if form.is_valid():
            clean_data = form.cleaned_data
            book_uri = request.build_absolute_uri(book.get_absolute_url())
            subject = '{} хочет поделиться с вами замечательной книгой!'.format(clean_data['name'],)
            body = '{} по ссылке {} \n\n Сообщение: \n {}'.format(book.name, book_uri, clean_data['message'])
            send_mail(subject, body, 'masha.afanaseva.29@mail.ru', [clean_data['email']])
            sent = True
    else:
        form = ShareBookForm()
    return render(request, 'book_search/share_book.html', {'form': form, 'sent': sent, 'book': book, 'is_bbc': is_bbc})


def show_tops(request):
    genres = models.Genres.objects.all()
    tops = models.Top.objects.all()
    return render(request, 'book_search/all_tops.html', {'tops': tops, 'genres': genres})


def add_rating(request, book_id, is_bbc):
    if request.method == 'POST':
        form = VotingForm(data=request.POST)
        if form.is_valid():
            new_rating = form.save(commit=False)
            new_rating.user_id = request.user
            if is_bbc == '1':
                new_rating.bbc_book_id = models.TopBBCBooks.objects.get(id=book_id)
            elif is_bbc == '0':
                new_rating.book_id = models.Book.objects.get(id=book_id)
            else:
                new_rating.top_book_id = models.BookInTop.objects.get(id=book_id)
            new_rating.value = form.cleaned_data.get('value')
            new_rating.save()
            return redirect('info_about_book', book_id, is_bbc)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)


def read(request, book_id, is_bbc):
    if request.method == 'POST':
        form = ReadForm(data=request.POST)
        if form.is_valid():
            read = form.save(commit=False)
            read.user_id = request.user
            if is_bbc == '1':
                read.bbc_book_id = models.TopBBCBooks.objects.get(id=book_id)
            elif is_bbc == '0':
                read.book_id = models.Book.objects.get(id=book_id)
            else:
                read.top_book_id = models.BookInTop.objects.get(id=book_id)
            read.value = form.cleaned_data.get('is_read')
            read.save()
            return redirect('info_about_book', book_id, is_bbc)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)


@login_required
def personal(request):
    genres = models.Genres.objects.all()
    user = request.user
    try:
        is_read = models.Read.objects.filter(user_id=user)
    except Exception:
        is_read = None
    try:
        wish_list = models.WishList.objects.filter(user_id=user)
    except Exception:
        wish_list = None
    return render(request, 'book_search/personal.html', {'is_read': is_read, 'genres': genres, 'wish_list': wish_list})


def wish_list(request):
    genres = models.Genres.objects.all()
    user_wish_list = models.WishList.objects.filter(user_id=request.user)
    paginator = Paginator(user_wish_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'book_search/wish_list.html', {'page_obj': page_obj, 'genres': genres})


def read_list(request):
    genres = models.Genres.objects.all()
    user_read_list = models.Read.objects.filter(user_id=request.user)
    paginator = Paginator(user_read_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'book_search/book_you_read.html', {'page_obj': page_obj, 'genres': genres})


def add_book_into_wishlist(request, book_id, is_bbc):
    if is_bbc == '0':
        book = models.Book.objects.get(id=book_id)
        b = models.WishList(user_id=request.user, book_id=book)
    elif is_bbc == '1':
        book = models.TopBBCBooks.objects.get(id=book_id)
        b = models.WishList(user_id=request.user, bbc_book_id=book)
    else:
        book = models.BookInTop.objects.get(id=book_id)
        b = models.WishList(user_id=request.user, top_book_id=book)
    b.save()
    return redirect('info_about_book', book_id, is_bbc)


def delete_book_from_wishlist(request, book_id, is_bbc):
    if is_bbc == '0':
        book = models.Book.objects.get(id=book_id)
        b = models.WishList.objects.get(user_id=request.user, book_id=book)
    elif is_bbc == '1':
        book = models.TopBBCBooks.objects.get(id=book_id)
        b = models.WishList.objects.get(user_id=request.user, bbc_book_id=book)
    else:
        book = models.BookInTop.objects.get(id=book_id)
        b = models.WishList.objects.get(user_id=request.user, top_book_id=book)
    b.delete()
    return redirect('user_wishlist')


def add_book(request):
    if request.method == 'POST':
        form = AddBook(request.POST, request.FILES)
        if form.is_valid():
            new_book = form.save(commit=False)
            new_book.save()
            return redirect('person')
    else:
        form = AddBook()
    return render(request, 'book_search/add_book.html', {'form': form})


def add_book_with_litres(request):
    query = request.GET.get('q')
    query = str(query).replace(' ', '%20')
    root = 'https://www.litres.ru/pages/rmd_search/?q=' + query
    response = requests.get(root)
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(str(response.text)), parser=parser)
    l_list = tree.xpath('//div[@class="books_box result_box"]//div[@class="art-item__name"]//a/@href')
    if not l_list:
        messages.error(request, 'Мы не можем добавить книгу автоматически, Вы можете добавить книгу вручную.')
        return redirect('add_book')
    else:
        l_list = l_list[0]
        link_litres = 'https://www.litres.ru' + l_list
        new_response = requests.get(link_litres)
        tree = etree.parse(StringIO(str(new_response.text)), parser=parser)
        book_name = tree.xpath('//div[@class="biblio_book_name biblio-book__title-block"]//h1/text()')[0]
        book_picture = tree.xpath('//div[@class="cover"]//img/@src')[0]
        book_genres = tree.xpath('//div[@class="biblio_book_info"]//ul//li')
        i = 1
        for div in book_genres:
            if i == 2:
                first_letters = div.xpath('.//a/span/text()')
                other_letters = div.xpath('.//a/text()')
                length = len(first_letters)
                genres = []
                for a in range(length):
                    genres.append(first_letters[a] + other_letters[a])
            i += 1
        author = tree.xpath('//div[@class="biblio_book_author"]//a/text()')
        book_author = ''
        for i in author:
            book_author += i + ', '
        book_author = list(book_author)
        book_author.pop()
        book_author.pop()
        book_author = ''.join(book_author)
        desc = tree.xpath('//div[@class="biblio_book_annotation"]//div[@itemprop="description"]//p/text()')
        book_description = ''
        for i in desc:
            book_description += i + '\n'
        book = list(models.Book.objects.filter(name=book_name, author=book_author))
        books = models.Book.objects.all()
        book_author_normalized = book_author.lower()
        authors = set()
        for book1 in books:
            authors.add(book1.author)
        authors = sorted(list(authors))
        for author in authors:
            author_normalized = author.lower()
            matcher = difflib.SequenceMatcher(None, author_normalized, book_author_normalized)
            if matcher.ratio() > 0.75:
                book_author = author
        if not book:
            for genre in genres:
                current_genres = models.Genres.objects.all()
                current_genres_names = []
                for cur_genre in current_genres:
                    current_genres_names.append(cur_genre.name)
                if genre not in current_genres_names:
                    g = models.Genres(name=genre)
                    g.save()
                p = requests.get(book_picture)
                genre = models.Genres.objects.get(name=genre)
                b = models.Book(name=book_name, author=book_author, description=book_description, genre_id=genre)
                name = urlparse(book_picture).path.split('/')[-1]
                b.image.save(name, ContentFile(p.content), save=True)
                b.save()
            messages.success(request, 'Книга успешно добавлена!')
            return redirect('person')
        else:
            messages.error(request, 'Книга уже зарегистрирована')
            return redirect('person')
