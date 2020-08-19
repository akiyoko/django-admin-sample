import csv
import os

from django.core.management.base import BaseCommand
from time import time

from addresses.models import Address

# 郵便番号データ（全国一括データ（加工済バージョン））
# http://zipcloud.ibsnet.co.jp/
INPUTS_DIR = os.path.join(os.path.dirname(__file__), 'inputs')
ADDRESSES_CSV_PATH = os.path.join(INPUTS_DIR, 'x-ken-all.csv')


class Command(BaseCommand):
    """郵便番号データインポート"""

    help = "Bulk import for all address records."

    def handle(self, *args, **options):
        _start = time()

        with open(ADDRESSES_CSV_PATH, encoding='shift_jis') as f:
            reader = csv.reader(f)
            addresses = [
                Address(
                    local_goverment_code=row[0],
                    postal_code_old=row[1],
                    postal_code=row[2],
                    prefecture_kana=row[3],
                    city_kana=row[4],
                    section_kana=row[5],
                    prefecture=row[6],
                    city=row[7],
                    section=row[8],
                    has_multiple_postal_codes=row[9],
                    has_banchi=row[10],
                    has_chome=row[11],
                    has_multiple_sections=row[12],
                    update_status=row[13],
                    update_reason=row[14],
                )
                for row in reader
            ]
        Address.objects.bulk_create(addresses)

        print(f'{len(addresses)} address records created in {time() - _start:.1f} secs.')
