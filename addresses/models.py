from django.db import models


class Address(models.Model):
    """住所マスタモデル"""

    class Meta:
        db_table = 'address'
        verbose_name = verbose_name_plural = '住所マスタ'

    APPLICABLE_CHOICES = (
        (1, '該当'),
        (0, '該当せず'),
    )

    UPDATE_STATUS_CHOICES = (
        (0, '変更なし'),
        (1, '変更あり'),
        (2, '廃止'),
    )

    UPDATE_REASON_CHOICES = (
        (0, '変更なし'),
        (1, '市政・区政・町政・分区・政令指定都市施行'),
        (2, '住居表示の実施'),
        (3, '区画整理'),
        (4, '郵便区調整等'),
        (5, '訂正'),
        (6, '廃止'),
    )

    local_goverment_code = models.IntegerField('全国地方公共団体コード')
    postal_code_old = models.CharField('旧郵便番号', max_length=255)
    postal_code = models.CharField('郵便番号', max_length=255)
    prefecture_kana = models.CharField('都道府県名カナ', max_length=255)
    city_kana = models.CharField('市区町村名カナ', max_length=255)
    section_kana = models.CharField('町域名カナ', max_length=255, null=True, blank=True)
    prefecture = models.CharField('都道府県名カナ', max_length=255)
    city = models.CharField('市区町村名', max_length=255)
    section = models.CharField('町域名', max_length=255, null=True, blank=True)
    has_multiple_postal_codes = models.SmallIntegerField('一町域が二以上の郵便番号で表される場合の表示',
                                                         choices=APPLICABLE_CHOICES)
    has_banchi = models.SmallIntegerField('小字毎に番地が起番されている町域の表示',
                                          choices=APPLICABLE_CHOICES)
    has_chome = models.SmallIntegerField('丁目を有する町域の場合の表示',
                                         choices=APPLICABLE_CHOICES)
    has_multiple_sections = models.SmallIntegerField('一つの郵便番号で二以上の町域を表す場合の表示',
                                                     choices=APPLICABLE_CHOICES)
    update_status = models.SmallIntegerField('更新の表示', choices=UPDATE_STATUS_CHOICES)
    update_reason = models.SmallIntegerField('変更理由', choices=UPDATE_REASON_CHOICES)

    def __str__(self):
        return f'{self.postal_code}/{self.prefecture}/{self.city}/{self.section}'
