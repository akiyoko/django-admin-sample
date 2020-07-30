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

    def create_books(self):
        # テストレコードを作成
        self.publisher = Publisher.objects.create(name='自費出版社')
        self.author = Author.objects.create(name='akiyoko')
        self.book = Book.objects.create(
            id=1,
            title='Django Book 1',
            price=1000,
            size='a4',
            publish_date=date(2020, 1, 1),
            publisher=self.publisher,
        )
        self.book2 = Book.objects.create(
            id=2,
            title='Django Book 2',
            price=2000,
            size='b5',
            publish_date=date(2020, 2, 1),
        )
        self.book2.authors.set([self.author])
        self.book3 = Book.objects.create(id=3, title='Book 3')
        self.books = [self.book, self.book2, self.book3]

    def test_show_page(self):
        """モデル一覧画面への画面遷移"""

        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)
        # モデル一覧画面に遷移
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')

    def test_page_items_if_result_list_is_empty(self):
        """モデル一覧画面の画面項目検証（検索結果が0件）

        以下の画面項目を確認する
        ・追加ボタンが表示される
        ・簡易検索フォームが表示される
        ・絞り込み（フィルタ）が表示される
        ・アクション一覧が表示されない
        ・検索結果表示テーブルが表示されない
        ・合計件数が「全 X 件」と表示される
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
        # 追加ボタンが表示されることを確認
        self.assertIsNotNone(page.add_button)
        # 簡易検索フォームが表示されることを確認
        self.assertIsNotNone(page.search_form)
        # 絞り込み（フィルタ）が表示されることを確認
        self.assertIsNotNone(page.filter)
        # アクション一覧が表示されないことを確認
        self.assertIsNone(page.action_list_texts)
        # 検索結果表示テーブルが表示されないことを確認
        self.assertIsNone(page.result_list)
        # 合計件数が表示されることを確認
        self.assertEqual(page.result_count_text, '全 0 件')

    def test_page_items_if_result_list_is_not_empty(self):
        """モデル一覧画面の画面項目検証（検索結果が0件でない）

        以下の画面項目を確認する
        ・追加ボタンが表示される
        ・簡易検索フォームが表示される
        ・絞り込み（フィルタ）が表示される
        ・アクション一覧が表示される
        ・検索結果表示テーブルが表示される
        ・合計件数が「全 X 件」と表示される
        """
        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # モデル一覧画面に遷移
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')

        # 画面表示項目を検証
        page = ChangeListPage(response.rendered_content)
        # 追加ボタンが表示されることを確認
        self.assertIsNotNone(page.add_button)
        # 簡易検索フォームが表示されることを確認
        self.assertIsNotNone(page.search_form)
        # 絞り込み（フィルタ）が表示されることを確認
        self.assertIsNotNone(page.filter)
        # アクション一覧
        self.assertEqual(
            page.action_list_texts,
            ['---------', '選択された 本 の削除', 'CSVダウンロード', '出版日を今日に更新']
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

        # モデル一覧画面で簡易検索を実行
        response = self.client.get(self.TARGET_URL + '?q=Book')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 3)
        self.assertEqual(
            [obj.id for obj in response.context_data['cl'].result_list],
            [self.book.id, self.book2.id, self.book3.id]
        )

        response = self.client.get(self.TARGET_URL + '?q=Django')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 2)
        self.assertEqual(
            [obj.id for obj in response.context_data['cl'].result_list],
            [self.book.id, self.book2.id]
        )

    def test_search_by_price(self):
        """モデル一覧画面にて価格で簡易検索"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # モデル一覧画面で簡易検索を実行
        response = self.client.get(self.TARGET_URL + '?q=1000')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 1)
        self.assertEqual(
            [obj.id for obj in response.context_data['cl'].result_list],
            [self.book.id]
        )

    def test_search_by_publisher_name(self):
        """モデル一覧画面にて出版社名で簡易検索"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # モデル一覧画面で簡易検索を実行
        response = self.client.get(self.TARGET_URL + '?q=自費出版社')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 1)
        self.assertEqual(
            [obj.id for obj in response.context_data['cl'].result_list],
            [self.book.id]
        )

    def test_search_by_author_name(self):
        """モデル一覧画面にて著者名で簡易検索"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # モデル一覧画面で簡易検索を実行
        response = self.client.get(self.TARGET_URL + '?q=akiyoko')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 1)
        self.assertEqual(
            [obj.id for obj in response.context_data['cl'].result_list],
            [self.book2.id]
        )

    def test_filter_by_size(self):
        """モデル一覧画面にてサイズで絞り込み"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # サイズを「A4 - 210 x 297 mm」で絞り込み
        response = self.client.get(self.TARGET_URL + '?size__exact=a4')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 1)
        self.assertEqual(
            [obj.id for obj in response.context_data['cl'].result_list],
            [self.book.id]
        )

        # サイズを「B5 - 182 x 257 mm」で絞り込み
        response = self.client.get(self.TARGET_URL + '?size__exact=b5')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 1)
        self.assertEqual(
            [obj.id for obj in response.context_data['cl'].result_list],
            [self.book2.id]
        )

    def test_filter_by_prices(self):
        """モデル一覧画面にて価格で絞り込み"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # 価格を「1,000円未満」で絞り込み
        response = self.client.get(self.TARGET_URL + '?prices=%2C1000')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 0)

        # 価格を「1,000円以上 2,000円未満」で絞り込み
        response = self.client.get(self.TARGET_URL + '?prices=1000%2C2000')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 1)
        self.assertEqual(
            [obj.id for obj in response.context_data['cl'].result_list],
            [self.book.id]
        )

        # 価格を「2,000円以上」で絞り込み
        response = self.client.get(self.TARGET_URL + '?prices=2000%2C')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['cl'].result_count, 1)
        self.assertEqual(
            [obj.id for obj in response.context_data['cl'].result_list],
            [self.book2.id]
        )

    def test_actions_delete_selected(self):
        """モデルのモデル一覧画面にて一括削除を実行"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # アクション一覧から一括削除を実行
        response = self.client.post(
            self.TARGET_URL,
            {
                'action': 'delete_selected',
                '_selected_action': [b.id for b in self.books],
            },
        )
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/delete_selected_confirmation.html')

    @patch('shop.admin.timezone.localdate', return_value=date(2020, 10, 1))
    def test_actions_publish_today(self, _mock_localdate):
        """モデルのモデル一覧画面にて「出版日を今日に更新」を実行"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # アクション一覧からCSVダウンロードを実行
        response = self.client.post(
            self.TARGET_URL,
            {
                'action': 'publish_today',
                '_selected_action': [self.book.id],
            },
            follow=True,
        )
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        # レコードが更新されていることを確認
        book = Book.objects.get(pk=self.book.pk)
        self.assertEqual(book.publish_date, date(2020, 10, 1))

    @patch('django.utils.timezone.now',
           return_value=datetime(2020, 10, 1, tzinfo=timezone.utc))
    def test_actions_download_as_csv(self, _mock_now):
        """モデルのモデル一覧画面でCSVダウンロード"""

        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # アクション一覧からCSVダウンロードを実行
        response = self.client.post(
            self.TARGET_URL,
            {
                'action': 'download_as_csv',
                '_selected_action': [b.id for b in self.books],
            },
        )
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
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
        """モデル一覧画面への画面遷移

        画面項目の検証
        ・追加ボタンが表示されないことを検証する
        ・アクション一覧にCSVダウンロードのみが表示されていること"""

        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # モデル一覧画面に遷移
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')

        # 画面表示項目を検証
        page = ChangeListPage(response.rendered_content)
        # 追加ボタンが表示されないこと
        self.assertIsNone(page.add_button)
        # 簡易検索フォームが表示されていること
        self.assertIsNotNone(page.search_form)
        # 絞り込み（フィルタ）が表示されていること
        self.assertIsNotNone(page.filter)
        # アクション一覧
        self.assertEqual(page.action_list_texts, ['---------', 'CSVダウンロード'])
        # 検索結果表示テーブル
        # 検索結果表示テーブルが表示されていること
        self.assertIsNotNone(page.result_list)

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
    #             '_selected_action': [b.id for b in self.books],
    #         },
    #         follow=True,
    #     )
    #     # レスポンスを検証
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'admin/change_list.html')
    #     # TODO
    #     # 画面表示項目を検証
    #     page = ChangeListPage(response.rendered_content)
    #     # 追加ボタンが表示されていること
    #     self.assertEqual(page.warning_message, '操作が選択されていません。')

    # ...（略）...


class TestAdminBookChangeListByAnonymousUser(TestCase):
    """管理サイトのBookモデル一覧画面のユニットテスト（未ログインユーザーの場合）"""

    TARGET_URL = reverse('admin:shop_book_changelist')

    def test_show_page(self):
        """モデル一覧画面への画面遷移

        - ログイン画面にリダイレクトされることを検証する"""

        # モデル一覧画面に遷移（リダイレクトをともなう場合は follow=True を指定）
        response = self.client.get(self.TARGET_URL, follow=True)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/login.html')
