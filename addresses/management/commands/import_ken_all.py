from time import time

try:
    import pandas as pd
except ImportError:
    raise ImportError("You need install pandas.")

from django.core.management.base import BaseCommand

from addresses.models import Address

# 郵便番号データ（全国一括データ（加工済バージョン））
# http://zipcloud.ibsnet.co.jp/
ADDRESSES_CSV_FILE_PATH = 'addresses/management/commands/inputs/x-ken-all.csv'


class Command(BaseCommand):
    """郵便番号データインポート"""

    help = "Bulk import for address records."

    def handle(self, *args, **options):
        _start = time()

        df = pd.read_csv(
            ADDRESSES_CSV_FILE_PATH,
            names=(
                'local_goverment_code',
                'postal_code_old',
                'postal_code',
                'prefecture_kana',
                'city_kana',
                'town_area_kana',
                'prefecture',
                'city',
                'town_area',
                'is_one_town_by_multi_postal_code',
                'is_need_small_area_address',
                'is_chome',
                'is_multi_town_by_one_postal_code',
                'update_status',
                'update_reason',
            ),
            dtype=str,  # 指定しないと、例えば「0600000」が float 扱いになり「600000」に変換されてしまう
            keep_default_na=False,  # NaN を空文字に変換
            encoding='shift_jis',  # x-ken-all.csv のエンコード
        )

        addresses = [
            Address(
                local_goverment_code=row['local_goverment_code'],
                postal_code_old=row['postal_code_old'],
                postal_code=row['postal_code'],
                prefecture_kana=row['prefecture_kana'],
                city_kana=row['city_kana'],
                town_area_kana=row['town_area_kana'],
                prefecture=row['prefecture'],
                city=row['city'],
                town_area=row['town_area'],
                is_one_town_by_multi_postal_code=row[
                    'is_one_town_by_multi_postal_code'],
                is_need_small_area_address=row['is_need_small_area_address'],
                is_chome=row['is_chome'],
                is_multi_town_by_one_postal_code=row[
                    'is_multi_town_by_one_postal_code'],
                update_status=row['update_status'],
                update_reason=row['update_reason'],
            )
            for index, row in df.iterrows()
        ]

        Address.objects.bulk_create(addresses)
        print(
            f'{len(addresses)} address records created in {time() - _start:.2f} secs.')
