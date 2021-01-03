from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class TopBBCBooks(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    author = models.CharField(max_length=200, verbose_name='Автор')
    picture = models.ImageField(upload_to='top200/%Y/%m/%d/', blank=True, null=True, verbose_name='Изображение')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    def get_absolute_url(self):
        return '/book/{}/1'.format(self.id)

    def __str__(self):
        return self.name


class Genres(models.Model):
    name = models.CharField(max_length=200, verbose_name='Жанр')

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    author = models.CharField(max_length=200, verbose_name='Автор')
    genre_id = models.ForeignKey(Genres, verbose_name='Жанр', on_delete=models.CASCADE)
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    image = models.ImageField(verbose_name='Изображение', upload_to='books/%Y/%m/%d', blank=True, null=True)

    def get_absolute_url(self):
        return '/book/{}/0'.format(self.id)

    def __str__(self):
        return '{} by {}. id={}'.format(self.name, self.author, self.id)


class Marketplace(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    picture = models.ImageField(verbose_name='Изображение', upload_to='marketplaces/%Y/%m/%d')


class TopType(models.Model):
    name = models.CharField(max_length=200, verbose_name='тип топа')

    def __str__(self):
        return self.name


class BookInTop(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    author = models.CharField(max_length=200, verbose_name='Автор')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    image = models.ImageField(verbose_name='Изображение', upload_to='books/%Y/%m/%d', blank=True, null=True)
    place_in_top = models.IntegerField(verbose_name='Место в топе', default=1)

    def __str__(self):
        return '{}. place={}'.format(self.name, self.place_in_top)

    def get_absolute_url(self):
        return '/book/{}/2'.format(self.id)


class Top(models.Model):
    name = models.CharField(max_length=200, verbose_name='название топа')
    top_type = models.ForeignKey(TopType, verbose_name='тип топа', on_delete=models.CASCADE)
    author_id = models.ForeignKey(User, verbose_name='автор топа', on_delete=models.CASCADE)
    books = models.ManyToManyField(BookInTop)

    def __str__(self):
        return '{} by {}'.format(self.name, self.author_id)


class Comment(models.Model):
    top_book_id = models.ForeignKey(BookInTop, verbose_name='К книге (top)', on_delete=models.SET_NULL, blank=True, null=True)
    book_id = models.ForeignKey(Book, verbose_name='К книге', on_delete=models.CASCADE, blank=True, null=True)
    bbc_book_id = models.ForeignKey(TopBBCBooks, verbose_name='К книге (BBC)', on_delete=models.CASCADE, blank=True, null=True)
    author_id = models.ForeignKey(User, verbose_name='Автор комментария', on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата написания')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.text[:200]


class VoteStar(models.Model):
    value = models.SmallIntegerField(verbose_name='Значение')

    class Meta:
        ordering = ['-value']

    def __str__(self):
        return '{}'.format(self.value)


class Vote(models.Model):
    value = models.ForeignKey(VoteStar, verbose_name='Рейтинг', on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор оценки')
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='К книге', blank=True, null=True)
    top_book_id = models.ForeignKey(BookInTop, on_delete=models.CASCADE, verbose_name='К книге (топ)', blank=True,
                                    null=True)
    bbc_book_id = models.ForeignKey(TopBBCBooks, verbose_name='К книге (BBC)', on_delete=models.CASCADE, blank=True,
                                    null=True)
    voted_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user_id', 'book_id'], ['user_id', 'top_book_id'], ['user_id', 'bbc_book_id']]


class Read(models.Model):
    is_read = models.BooleanField(verbose_name='Прочитано')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор оценки')
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='К книге', blank=True, null=True)
    top_book_id = models.ForeignKey(BookInTop, on_delete=models.CASCADE, verbose_name='К книге (топ)', blank=True,
                                    null=True)
    bbc_book_id = models.ForeignKey(TopBBCBooks, verbose_name='К книге (BBC)', on_delete=models.CASCADE, blank=True,
                                    null=True)
    voted_on = models.DateTimeField(auto_now=True)


class WishList(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор списка', null=True, blank=True)
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='К книге', null=True, blank=True)
    top_book_id = models.ForeignKey(BookInTop, on_delete=models.CASCADE, verbose_name='К книге (топ)', blank=True,
                                    null=True)
    bbc_book_id = models.ForeignKey(TopBBCBooks, verbose_name='К книге (BBC)', on_delete=models.CASCADE, blank=True,
                                    null=True)