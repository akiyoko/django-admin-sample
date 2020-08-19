from django.db import models


class Address(models.Model):
    """住所マスタモデル"""

    class Meta:
        db_table = 'address'
        verbose_name = verbose_name_plural = '住所マスタ'

    local_goverment_code = models.IntegerField('全国地方公共団体コード')
    postal_code_old = models.CharField('旧郵便番号', max_length=255)
    postal_code = models.CharField('郵便番号', max_length=255)
    prefecture_kana = models.CharField('都道府県名カナ', max_length=255)
    city_kana = models.CharField('市区町村名カナ', max_length=255)
    section_kana = models.CharField('町域名カナ', max_length=255, null=True, blank=True)
    prefecture = models.CharField('都道府県名カナ', max_length=255)
    city = models.CharField('市区町村名', max_length=255)
    section = models.CharField('町域名', max_length=255, null=True, blank=True)
    has_multiple_postal_codes = models.BooleanField('一町域が二以上の郵便番号で表される場合の表示',
                                                    null=True, blank=True)
    has_banchi = models.BooleanField('小字毎に番地が起番されている町域の表示',
                                     null=True, blank=True)
    has_chome = models.BooleanField('丁目を有する町域の場合の表示', null=True, blank=True)
    has_multiple_sections = models.BooleanField('一つの郵便番号で二以上の町域を表す場合の表示',
                                                null=True, blank=True)
    update_status = models.CharField('更新の表示', max_length=1, null=True, blank=True)
    update_reason = models.CharField('変更理由', max_length=1, null=True, blank=True)

    def __str__(self):
        return f'{self.postal_code}/{self.prefecture}/{self.city}/{self.section}'
