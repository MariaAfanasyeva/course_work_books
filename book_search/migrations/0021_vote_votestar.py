# Generated by Django 3.1.4 on 2020-12-29 17:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('book_search', '0020_auto_20201228_1925'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoteStar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(verbose_name='Знвчение')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voted_on', models.DateTimeField(auto_now=True)),
                ('bbc_book_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='book_search.topbbcbooks', verbose_name='К книге (BBC)')),
                ('book_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book_search.book', verbose_name='К книге')),
                ('top_book_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book_search.bookintop', verbose_name='К книге (топ)')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор оценки')),
                ('value', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book_search.votestar', verbose_name='Рейтинг')),
            ],
            options={
                'unique_together': {('user_id', 'top_book_id'), ('user_id', 'bbc_book_id'), ('user_id', 'book_id')},
            },
        ),
    ]