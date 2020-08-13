# Generated by Django 2.2.15 on 2020-08-13 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('local_goverment_code', models.IntegerField(verbose_name='全国地方公共団体コード')),
                ('postal_code_old', models.CharField(max_length=255, verbose_name='旧郵便番号')),
                ('postal_code', models.CharField(max_length=255, verbose_name='郵便番号')),
                ('prefecture_kana', models.CharField(max_length=255, verbose_name='都道府県名カナ')),
                ('city_kana', models.CharField(max_length=255, verbose_name='市区町村名カナ')),
                ('town_area_kana', models.CharField(blank=True, max_length=255, null=True, verbose_name='町域名カナ')),
                ('prefecture', models.CharField(max_length=255, verbose_name='都道府県名カナ')),
                ('city', models.CharField(max_length=255, verbose_name='市区町村名')),
                ('town_area', models.CharField(blank=True, max_length=255, null=True, verbose_name='町域名')),
                ('is_one_town_by_multi_postal_code', models.BooleanField(blank=True, null=True, verbose_name='一町域が二以上の郵便番号で表される場合の表示')),
                ('is_need_small_area_address', models.BooleanField(blank=True, null=True, verbose_name='小字毎に番地が起番されている町域の表示')),
                ('is_chome', models.BooleanField(blank=True, null=True, verbose_name='丁目を有する町域の場合の表示')),
                ('is_multi_town_by_one_postal_code', models.BooleanField(blank=True, null=True, verbose_name='一つの郵便番号で二以上の町域を表す場合の表示')),
                ('update_status', models.CharField(blank=True, max_length=1, null=True, verbose_name='更新の表示')),
                ('update_reason', models.CharField(blank=True, max_length=1, null=True, verbose_name='変更理由')),
            ],
            options={
                'verbose_name': '住所マスタ',
                'verbose_name_plural': '住所マスタ',
                'db_table': 'address',
            },
        ),
    ]
