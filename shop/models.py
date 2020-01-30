from django.db import models


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

    SIZE_CHOICES = (
        ('b5', 'B5 - 182 x 257 mm'),
        ('a4', 'A4 - 210 x 297 mm'),
    )

    title = models.CharField('タイトル', max_length=255)
    image = models.ImageField('画像', null=True, blank=True)
    publisher = models.ForeignKey(Publisher, verbose_name='出版社', on_delete=models.PROTECT,
                                  null=True, blank=True)
    authors = models.ManyToManyField(Author, verbose_name='著者', blank=True)
    price = models.PositiveIntegerField('価格', null=True, blank=True, default=0)
    size = models.CharField('サイズ', max_length=2, choices=SIZE_CHOICES, null=True, blank=True)
    description = models.TextField('概要', null=True, blank=True)
    publish_date = models.DateField('出版日', null=True, blank=True)

    def __str__(self):
        return self.title
