import csv
import io
from datetime import date, datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .lxml_helpers import ChangeListPage
from ..models import Author, Book, Publisher

User = get_user_model()


class TestAdminBookChangeList(TestCase):
    """管理サイトのBookモデル一覧画面のユニットテスト（システム管理者の場合）"""

    TARGET_URL = reverse('admin:shop_book_changelist')
    PASSWORD = 'pass12345'

    def setUp(self):
        # テストユーザー（システム管理者）を作成
        self.user = User.objects.create_superuser(
            'admin', 'admin@example.com', self.PASSWORD)

        # django.utils.timezone.now() が常に同じ日時を返すようにモック化
        self.now = datetime(2020, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
        patcher_now = patch(
            'django.utils.timezone.now',
            return_value=self.now,
        )
        self.mock_now = patcher_now.start()
        self.addCleanup(patcher_now.stop)

    def create_books(self):
        # テストレコードを作成
        self.publisher = Publisher.objects.create(name='自費出版社')
        self.author = Author.objects.create(name='akiyoko')
        self.book = Book.objects.create(
            title='Django Book 1',
            price=1000,
            size='a4',
            publish_date=date(2020, 1, 1),
            publisher=self.publisher,
        )
        self.book2 = Book.objects.create(
            title='Django Book 2',
            price=2000,
            size='b5',
            publish_date=date(2020, 2, 1),
        )
        self.book2.authors.set([self.author])
        self.book3 = Book.objects.create(title='Book 3')
        self.books = [self.book, self.book2, self.book3]

    def test_show_page(self):
        """モデル一覧画面への画面遷移"""

        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)
        # モデル一覧画面に遷移するためのリクエストを実行
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')

    def test_page_items_if_result_list_is_empty(self):
        """モデル一覧画面の画面項目検証（検索結果が0件の場合）

        以下の画面項目を確認する
        ・追加ボタンが表示されていること
        ・簡易検索フォームが表示されていること
        ・絞り込み（フィルタ）が表示されていること
        ・アクション一覧が表示されていないこと
        ・検索結果表示テーブルが表示されていないこと
        ・合計件数が「全 0 件」と表示されていること
        """
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)
        # モデル一覧画面に遷移するためのリクエストを実行
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')

        # 画面表示項目を検証
        page = ChangeListPage(response.rendered_content)
        # 追加ボタンが表示されていることを確認
        self.assertIsNotNone(page.add_button)
        # 簡易検索フォームが表示されていることを確認
        self.assertIsNotNone(page.search_form)
        # 絞り込み（フィルタ）が表示されていることを確認
        self.assertEqual(
            page.filter_headers,
            ['サイズ で絞り込む', '価格 で絞り込む']
        )
        self.assertEqual(
            page.filter_choices_texts[0],
            ['全て', 'A4 - 210 x 297 mm', 'B5 - 182 x 257 mm']
        )
        self.assertEqual(
            page.filter_choices_texts[1],
            ['全て', '1,000円未満', '1,000円以上 2,000円未満', '2,000円以上']
        )
        # アクション一覧が表示されていないことを確認
        self.assertIsNone(page.action_list_texts)
        # 検索結果表示テーブルが表示されていないことを確認
        self.assertIsNone(page.result_list)
        # 合計件数が表示されていることを確認
        self.assertEqual(page.result_count_text, '全 0 件')

    def test_page_items_if_result_list_is_not_empty(self):
        """モデル一覧画面の画面項目検証（検索結果が0件でない場合）

        以下の画面項目を確認する
        ・追加ボタンが表示されていること
        ・簡易検索フォームが表示されていること
        ・絞り込み（フィルタ）が表示されていること
        ・アクション一覧が表示されていること
        ・検索結果表示テーブルが表示されていること
        ・合計件数が「全 n 件」と表示されていること
        """
        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # モデル一覧画面に遷移するためのリクエストを実行
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')

        # 画面表示項目を検証
        page = ChangeListPage(response.rendered_content)
        # 追加ボタンが表示されていることを確認
        self.assertIsNotNone(page.add_button)
        # 簡易検索フォームが表示されていることを確認
        self.assertIsNotNone(page.search_form)
        # 絞り込み（フィルタ）が表示されていることを確認
        self.assertIsNotNone(page.filter_headers)
        # アクション一覧
        self.assertEqual(
            page.action_list_texts,
            ['---------', '選択された 本 の削除', 'CSVダウンロード',
             '出版日を今日に更新']
        )
        # 検索結果表示テーブル
        self.assertEqual(
            page.result_list_head_texts,
            ['ID', 'タイトル', '価格', 'サイズ', '出版日']
        )
        self.assertEqual(len(page.result_list_rows_texts), 3)
        self.assertEqual(
            page.result_list_rows_texts[0],
            ['Django Book 1', '1,000 円', 'A4 - 210 x 297 mm', '2020年1月1日']
        )
        self.assertEqual(
            page.result_list_rows_texts[1],
            ['Django Book 2', '2,000 円', 'B5 - 182 x 257 mm', '2020年2月1日']
        )
        self.assertEqual(
            page.result_list_rows_texts[2],
            ['Book 3', '-', '-', '-']
        )
        # 合計件数
        self.assertEqual(page.result_count_text, '全 3 件')

    def test_search_by_title(self):
        """モデル一覧画面にてタイトルで簡易検索"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # 「Book」で簡易検索するためのリクエストを実行
        response = self.client.get(self.TARGET_URL + '?q=Book')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 3)
        self.assertEqual(
            [obj.id for obj in response.context_data['cl'].result_list],
            [self.book.pk, self.book2.pk, self.book3.pk]
        )

        # 「Django」で簡易検索するためのリクエストを実行
        response = self.client.get(self.TARGET_URL + '?q=Django')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 2)
        self.assertEqual(
            [obj.pk for obj in response.context_data['cl'].result_list],
            [self.book.pk, self.book2.pk]
        )

    def test_search_by_price(self):
        """モデル一覧画面にて価格で簡易検索"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # 「1000」で簡易検索するためのリクエストを実行
        response = self.client.get(self.TARGET_URL + '?q=1000')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 1)
        self.assertEqual(
            [obj.pk for obj in response.context_data['cl'].result_list],
            [self.book.pk]
        )

    def test_search_by_publisher_name(self):
        """モデル一覧画面にて出版社名で簡易検索"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # 「自費出版社」で簡易検索するためのリクエストを実行
        response = self.client.get(self.TARGET_URL + '?q=自費出版社')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 1)
        self.assertEqual(
            [obj.pk for obj in response.context_data['cl'].result_list],
            [self.book.pk]
        )

    def test_search_by_author_name(self):
        """モデル一覧画面にて著者名で簡易検索"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # 「akiyoko」で簡易検索するためのリクエストを実行
        response = self.client.get(self.TARGET_URL + '?q=akiyoko')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 1)
        self.assertEqual(
            [obj.pk for obj in response.context_data['cl'].result_list],
            [self.book2.pk]
        )

    def test_filter_by_size(self):
        """モデル一覧画面にてサイズで絞り込み"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # サイズを「A4 - 210 x 297 mm」で絞り込むためのリクエストを実行
        response = self.client.get(self.TARGET_URL + '?size__exact=a4')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 1)
        self.assertEqual(
            [obj.pk for obj in response.context_data['cl'].result_list],
            [self.book.pk]
        )

        # サイズを「B5 - 182 x 257 mm」で絞り込むためのリクエストを実行
        response = self.client.get(self.TARGET_URL + '?size__exact=b5')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 1)
        self.assertEqual(
            [obj.pk for obj in response.context_data['cl'].result_list],
            [self.book2.pk]
        )

    def test_filter_by_price_ranges(self):
        """モデル一覧画面にて価格で絞り込み"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # 価格を「1,000円未満」で絞り込むためのリクエストを実行
        response = self.client.get(self.TARGET_URL + '?prices=%2C1000')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 0)

        # 価格を「1,000円以上 2,000円未満」で絞り込むためのリクエストを実行
        response = self.client.get(self.TARGET_URL + '?prices=1000%2C2000')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 1)
        self.assertEqual(
            [obj.pk for obj in response.context_data['cl'].result_list],
            [self.book.pk]
        )

        # 価格を「2,000円以上」で絞り込むためのリクエストを実行
        response = self.client.get(self.TARGET_URL + '?prices=2000%2C')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 1)
        self.assertEqual(
            [obj.pk for obj in response.context_data['cl'].result_list],
            [self.book2.pk]
        )

    def test_actions_delete_selected(self):
        """モデルのモデル一覧画面にて一括削除を実行"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # アクション一覧の一括削除を実行するためのリクエストを実行
        response = self.client.post(
            self.TARGET_URL,
            {
                'action': 'delete_selected',
                '_selected_action': [book.pk for book in self.books],
            },
            follow=True,
        )
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'admin/delete_selected_confirmation.html')

    def test_actions_publish_today(self):
        """モデルのモデル一覧画面にて「出版日を今日に更新」を実行"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # アクション一覧の「出版日を今日に更新」を実行するためのリクエストを実行
        response = self.client.post(
            self.TARGET_URL,
            {
                'action': 'publish_today',
                '_selected_action': [self.book.pk],
            },
            follow=True,
        )
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')
        # レコードが更新されていることを確認
        book = Book.objects.get(pk=self.book.pk)
        self.assertEqual(book.publish_date, date(2020, 10, 1))

    def test_actions_download_as_csv(self):
        """モデルのモデル一覧画面にて「CSVダウンロード」を実行"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # アクション一覧の「CSVダウンロード」を実行するためのリクエストを実行
        response = self.client.post(
            self.TARGET_URL,
            {
                'action': 'download_as_csv',
                '_selected_action': [book.pk for book in self.books],
            },
        )
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        # CSVファイルの内容を検証
        csv_reader = csv.reader(io.StringIO(response.content.decode('utf-8')))
        rows = list(csv_reader)
        header = rows.pop(0)
        self.assertEqual(
            header,
            ['id', 'title', 'image', 'publisher', 'price', 'size',
             'description', 'publish_date', 'created_by', 'created_at']
        )
        self.assertEqual(len(rows), 3)
        self.assertEqual(
            rows[0],
            ['1', 'Django Book 1', '', '自費出版社', '1000', 'a4',
             '', '2020-01-01', '', '2020-10-01 00:00:00+00:00']
        )
        self.assertEqual(
            rows[1],
            ['2', 'Django Book 2', '', '', '2000', 'b5',
             '', '2020-02-01', '', '2020-10-01 00:00:00+00:00']
        )
        self.assertEqual(
            rows[2],
            ['3', 'Book 3', '', '', '', '',
             '', '', '', '2020-10-01 00:00:00+00:00']
        )

    # ...（略）...


class TestAdminBookChangeListByViewStaff(TestCase):
    """管理サイトのBookモデル一覧画面のユニットテスト（閲覧用スタッフの場合）"""

    TARGET_URL = reverse('admin:shop_book_changelist')
    PASSWORD = 'pass12345'

    def setUp(self):
        # テストユーザー（閲覧用スタッフ）を作成
        self.user = User.objects.create_user(
            'staff', 'staff@example.com', self.PASSWORD, is_staff=True)
        self.user.user_permissions.set(
            Permission.objects.filter(codename='view_book'))

        # テストデータを作成
        self.books = [
            Book.objects.create(title='Book 1'),
        ]

    def test_show_page(self):
        """モデル一覧画面への画面遷移"""

        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # モデル一覧画面に遷移
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')

    def test_page_items(self):
        """モデル一覧画面の画面項目検証（検索結果が0件でない場合）

        以下の画面項目を確認する
        ・追加ボタンが表示されていないこと
        ・アクション一覧に「CSVダウンロード」のみが表示されていること
        """

        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # モデル一覧画面に遷移
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')

        # 画面表示項目を検証
        page = ChangeListPage(response.rendered_content)
        # 追加ボタンが表示されていないことを確認
        self.assertIsNone(page.add_button)
        # 簡易検索フォームが表示されていることを確認
        self.assertIsNotNone(page.search_form)
        # 絞り込み（フィルタ）が表示されていることを確認
        self.assertEqual(
            page.filter_headers,
            ['サイズ で絞り込む', '価格 で絞り込む']
        )
        self.assertEqual(
            page.filter_choices_texts[0],
            ['全て', 'A4 - 210 x 297 mm', 'B5 - 182 x 257 mm']
        )
        self.assertEqual(
            page.filter_choices_texts[1],
            ['全て', '1,000円未満', '1,000円以上 2,000円未満', '2,000円以上']
        )
        # アクション一覧に「CSVダウンロード」のみが表示されていることを確認
        self.assertEqual(
            page.action_list_texts, ['---------', 'CSVダウンロード'])
        # 検索結果表示テーブルが表示されていること
        self.assertEqual(
            page.result_list_head_texts,
            ['ID', 'タイトル', '価格', 'サイズ', '出版日']
        )
        self.assertEqual(len(page.result_list_rows_texts), 1)
        self.assertEqual(
            page.result_list_rows_texts[0],
            ['Book 1', '-', '-', '-']
        )
        # 合計件数
        self.assertEqual(page.result_count_text, '全 1 件')

    # def test_actions_delete_selected(self):
    #     """モデルのモデル一覧画面で一括削除するとエラー"""
    #
    #     # ログイン
    #     self.client.login(username=self.user.username, password=self.PASSWORD)
    #
    #     # モデル一覧画面のアクション一覧から一括削除を実行
    #     response = self.client.post(
    #         self.TARGET_URL,
    #         {
    #             'action': 'delete_selected',
    #             '_selected_action': [book.pk for book in self.books],
    #         },
    #         follow=True,
    #     )
    #     # レスポンスを検証
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'admin/change_list.html')
    #     # 画面表示項目を検証
    #     page = ChangeListPage(response.rendered_content)
    #     # TODO
    #     self.assertEqual(page.warning_message, '操作が選択されていません。')

    # ...（略）...


class TestAdminBookChangeListByAnonymousUser(TestCase):
    """管理サイトのBookモデル一覧画面のユニットテスト（未ログインユーザーの場合）"""

    TARGET_URL = reverse('admin:shop_book_changelist')

    def test_show_page(self):
        """モデル一覧画面への画面遷移

        ログイン画面にリダイレクトされることを確認する"""

        # モデル一覧画面に遷移するためのリクエストを実行
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertRedirects(
            response, '/admin/login/?next=/admin/shop/book/')
