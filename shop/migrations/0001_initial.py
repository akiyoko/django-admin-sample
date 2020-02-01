# Generated by Django 2.2.9 on 2020-01-31 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
            name='Publisher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='出版社名')),
            ],
            options={
                'verbose_name': '出版社',
                'verbose_name_plural': '出版社',
                'db_table': 'publisher',
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='タイトル')),
                ('image', models.ImageField(blank=True, null=True, upload_to='', verbose_name='画像')),
                ('price', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='価格')),
                ('size', models.CharField(blank=True, choices=[('a4', 'A4 - 210 x 297 mm'), ('b5', 'B5 - 182 x 257 mm')], max_length=2, null=True, verbose_name='サイズ')),
                ('description', models.TextField(blank=True, null=True, verbose_name='概要')),
                ('publish_date', models.DateField(blank=True, null=True, verbose_name='出版日')),
                ('authors', models.ManyToManyField(blank=True, to='shop.Author', verbose_name='著者')),
                ('publisher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='shop.Publisher', verbose_name='出版社')),
            ],
            options={
                'verbose_name': '本',
                'verbose_name_plural': '本',
                'db_table': 'book',
            },
        ),
    ]
