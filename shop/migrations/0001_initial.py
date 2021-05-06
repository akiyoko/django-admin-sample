# Generated by Django 2.2.15 on 2021-05-06 03:45

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='著者名')),
            ],
            options={
                'verbose_name': '著者',
                'verbose_name_plural': '著者',
                'db_table': 'author',
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='タイトル')),
                ('image', models.ImageField(blank=True, max_length=255, null=True, upload_to='', verbose_name='画像')),
                ('price', models.PositiveIntegerField(blank=True, null=True, verbose_name='価格')),
                ('size', models.CharField(blank=True, choices=[('a4', 'A4 - 210 x 297 mm'), ('b5', 'B5 - 182 x 257 mm')], max_length=2, null=True, verbose_name='サイズ')),
                ('description', models.TextField(blank=True, null=True, verbose_name='概要')),
                ('publish_date', models.DateField(blank=True, null=True, verbose_name='出版日')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='登録日時')),
                ('authors', models.ManyToManyField(blank=True, to='shop.Author', verbose_name='著者')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='登録ユーザー')),
            ],
            options={
                'verbose_name': '本',
                'verbose_name_plural': '本',
                'db_table': 'book',
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='出版社名')),
                ('postal_code', models.CharField(blank=True, max_length=8, null=True, validators=[django.core.validators.RegexValidator(message='郵便番号の形式になっていません。', regex='^\\d{3}-\\d{4}$')], verbose_name='郵便番号')),
                ('prefecture', models.CharField(blank=True, choices=[('北海道', '北海道'), ('青森県', '青森県'), ('岩手県', '岩手県'), ('宮城県', '宮城県'), ('秋田県', '秋田県'), ('山形県', '山形県'), ('福島県', '福島県'), ('茨城県', '茨城県'), ('栃木県', '栃木県'), ('群馬県', '群馬県'), ('埼玉県', '埼玉県'), ('千葉県', '千葉県'), ('東京都', '東京都'), ('神奈川県', '神奈川県'), ('新潟県', '新潟県'), ('富山県', '富山県'), ('石川県', '石川県'), ('福井県', '福井県'), ('山梨県', '山梨県'), ('長野県', '長野県'), ('岐阜県', '岐阜県'), ('静岡県', '静岡県'), ('愛知県', '愛知県'), ('三重県', '三重県'), ('滋賀県', '滋賀県'), ('京都府', '京都府'), ('大阪府', '大阪府'), ('兵庫県', '兵庫県'), ('奈良県', '奈良県'), ('和歌山県', '和歌山県'), ('鳥取県', '鳥取県'), ('島根県', '島根県'), ('岡山県', '岡山県'), ('広島県', '広島県'), ('山口県', '山口県'), ('徳島県', '徳島県'), ('香川県', '香川県'), ('愛媛県', '愛媛県'), ('高知県', '高知県'), ('福岡県', '福岡県'), ('佐賀県', '佐賀県'), ('長崎県', '長崎県'), ('熊本県', '熊本県'), ('大分県', '大分県'), ('宮崎県', '宮崎県'), ('鹿児島県', '鹿児島県'), ('沖縄県', '沖縄県')], max_length=255, null=True, verbose_name='都道府県')),
                ('address_1', models.CharField(blank=True, max_length=255, null=True, verbose_name='住所1')),
                ('address_2', models.CharField(blank=True, max_length=255, null=True, verbose_name='住所2')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator(message='電話番号の形式になっていません。', regex='^0\\d{1,4}-\\d{1,4}-\\d{4}$')], verbose_name='電話番号')),
            ],
            options={
                'verbose_name': '出版社',
                'verbose_name_plural': '出版社',
                'db_table': 'publisher',
            },
        ),
        migrations.CreateModel(
            name='BookStock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0, verbose_name='在庫数')),
                ('book', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='shop.Book', verbose_name='本')),
            ],
            options={
                'verbose_name': '在庫',
                'verbose_name_plural': '在庫',
                'db_table': 'stock',
            },
        ),
        migrations.AddField(
            model_name='book',
            name='publisher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='shop.Publisher', verbose_name='出版社'),
        ),
        migrations.CreateModel(
            name='PublishedBook',
            fields=[
            ],
            options={
                'verbose_name': '本（発売中）',
                'verbose_name_plural': '本（発売中）',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('shop.book',),
        ),
        migrations.CreateModel(
            name='UnpublishedBook',
            fields=[
            ],
            options={
                'verbose_name': '本（未発売）',
                'verbose_name_plural': '本（未発売）',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('shop.book',),
        ),
    ]
