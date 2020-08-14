from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse

User = get_user_model()

postal_code_validator = RegexValidator(regex=r'^\d{3}-\d{4}$',
                                       message="郵便番号の形式になっていません。")
phone_number_validator = RegexValidator(regex=r'^0\d{1,4}-\d{1,4}-\d{4}$',
                                        message="電話番号の形式になっていません。")


class Publisher(models.Model):
    """出版社モデル"""

    class Meta:
        db_table = 'publisher'
        verbose_name = verbose_name_plural = '出版社'

    PREFECTURE_CHOICES = (
        ('北海道', '北海道'),
        ('青森県', '青森県'),
        ('岩手県', '岩手県'),
        ('宮城県', '宮城県'),
        ('秋田県', '秋田県'),
        ('山形県', '山形県'),
        ('福島県', '福島県'),
        ('茨城県', '茨城県'),
        ('栃木県', '栃木県'),
        ('群馬県', '群馬県'),
        ('埼玉県', '埼玉県'),
        ('千葉県', '千葉県'),
        ('東京都', '東京都'),
        ('神奈川県', '神奈川県'),
        ('新潟県', '新潟県'),
        ('富山県', '富山県'),
        ('石川県', '石川県'),
        ('福井県', '福井県'),
        ('山梨県', '山梨県'),
        ('長野県', '長野県'),
        ('岐阜県', '岐阜県'),
        ('静岡県', '静岡県'),
        ('愛知県', '愛知県'),
        ('三重県', '三重県'),
        ('滋賀県', '滋賀県'),
        ('京都府', '京都府'),
        ('大阪府', '大阪府'),
        ('兵庫県', '兵庫県'),
        ('奈良県', '奈良県'),
        ('和歌山県', '和歌山県'),
        ('鳥取県', '鳥取県'),
        ('島根県', '島根県'),
        ('岡山県', '岡山県'),
        ('広島県', '広島県'),
        ('山口県', '山口県'),
        ('徳島県', '徳島県'),
        ('香川県', '香川県'),
        ('愛媛県', '愛媛県'),
        ('高知県', '高知県'),
        ('福岡県', '福岡県'),
        ('佐賀県', '佐賀県'),
        ('長崎県', '長崎県'),
        ('熊本県', '熊本県'),
        ('大分県', '大分県'),
        ('宮崎県', '宮崎県'),
        ('鹿児島県', '鹿児島県'),
        ('沖縄県', '沖縄県'),
    )

    name = models.CharField('出版社名', max_length=255)
    postal_code = models.CharField('郵便番号', max_length=8, null=True, blank=True,
                                   validators=[postal_code_validator])
    prefecture = models.CharField('都道府県', max_length=255,
                                  choices=PREFECTURE_CHOICES,
                                  null=True, blank=True)
    address_1 = models.CharField('市区町村番地', max_length=255,
                                 null=True, blank=True)
    address_2 = models.CharField('建物名', max_length=255, null=True, blank=True)
    phone_number = models.CharField('電話番号', max_length=15,
                                    null=True, blank=True,
                                    validators=[phone_number_validator])

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
    publisher = models.ForeignKey(Publisher, verbose_name='出版社',
                                  on_delete=models.PROTECT, null=True, blank=True)
    authors = models.ManyToManyField(Author, verbose_name='著者', blank=True)
    price = models.PositiveIntegerField('価格', null=True, blank=True)
    size = models.CharField('サイズ', max_length=2, choices=SIZE_CHOICES,
                            null=True, blank=True)
    description = models.TextField('概要', null=True, blank=True)
    publish_date = models.DateField('出版日', null=True, blank=True)
    created_by = models.ForeignKey(User, verbose_name='登録ユーザー',
                                   on_delete=models.SET_NULL,
                                   null=True, blank=True, editable=False)
    created_at = models.DateTimeField('登録日時', auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # TODO
        return reverse('admin:shop_book_change', args=[self.id])


class PublishedBook(Book):
    """本（発売中）モデル"""

    class Meta:
        proxy = True
        verbose_name = verbose_name_plural = '本（発売中）'


class UnpublishedBook(Book):
    """本（未発売）モデル"""

    class Meta:
        proxy = True
        verbose_name = verbose_name_plural = '本（未発売）'


class BookStock(models.Model):
    """本の在庫モデル"""

    class Meta:
        db_table = 'stock'
        verbose_name = verbose_name_plural = '在庫'

    book = models.OneToOneField(Book, verbose_name='本', on_delete=models.CASCADE)
    quantity = models.IntegerField('在庫数', default=0)

    def __str__(self):
        return self.book.title
