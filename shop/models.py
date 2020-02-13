from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class Publisher(models.Model):
    """出版社モデル"""

    class Meta:
        db_table = 'publisher'
        verbose_name = verbose_name_plural = '出版社'

    name = models.CharField('出版社名', max_length=255)

    def __str__(self):
        return self.name


class Author(models.Model):
    """著者モデル"""

    class Meta:
        db_table = 'author'
        verbose_name = verbose_name_plural = '著者'

    name = models.CharField('著者名', max_length=255)

    def __str__(self):
        return self.name


class Book(models.Model):
    """本モデル"""

    class Meta:
        db_table = 'book'
        verbose_name = verbose_name_plural = '本'

    SIZE_A4 = 'a4'
    SIZE_B5 = 'b5'
    SIZE_CHOICES = (
        (SIZE_A4, 'A4 - 210 x 297 mm'),
        (SIZE_B5, 'B5 - 182 x 257 mm'),
    )

    title = models.CharField('タイトル', max_length=255)
    image = models.ImageField('画像', max_length=255, null=True, blank=True)
    publisher = models.ForeignKey(Publisher, verbose_name='出版社', on_delete=models.PROTECT,
                                  null=True, blank=True)
    authors = models.ManyToManyField(Author, verbose_name='著者', blank=True)
    price = models.PositiveIntegerField('価格', null=True, blank=True)
    size = models.CharField('サイズ', max_length=2, choices=SIZE_CHOICES, null=True, blank=True)
    description = models.TextField('概要', null=True, blank=True)
    publish_date = models.DateField('出版日', null=True, blank=True)
    created_by = models.ForeignKey(User, verbose_name='登録ユーザー', on_delete=models.SET_NULL,
                                   null=True, blank=True, editable=False)
    created_at = models.DateTimeField('登録日時', default=timezone.now, editable=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # TODO
        return reverse('admin:shop_book_change', args=[self.id])


class BookStock(models.Model):
    """本の在庫モデル"""

    class Meta:
        db_table = 'stock'
        verbose_name = verbose_name_plural = '在庫'

    book = models.OneToOneField(Book, verbose_name='本', on_delete=models.CASCADE)
    quantity = models.IntegerField('在庫数', default=0)

    def __str__(self):
        return self.book.title
