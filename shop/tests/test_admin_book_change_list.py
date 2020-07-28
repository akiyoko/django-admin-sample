from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from .lxml_helpers import ChangeListPage
from ..models import Book

User = get_user_model()


class TestAdminBookChangeList(TestCase):
    """管理サイトのBookモデル一覧画面のテスト（システム管理者の場合）"""

    TARGET_URL = reverse('admin:shop_book_changelist')
    PASSWORD = 'pass12345'

    def setUp(self):
        # テストユーザー（システム管理者）を作成
        self.user = User.objects.create_superuser(
            'admin', 'admin@example.com', self.PASSWORD)

    def create_books(self):
        # テストレコードを作成
        self.books = [
            Book.objects.create(
                title='Book 1',
                price=1000,
                size='a4',
                publish_date=datetime(2020, 1, 1)
            ),
            Book.objects.create(
                title='Book 2',
                price=2000,
                size='b5',
                publish_date=datetime(2020, 2, 1)
            ),
            Book.objects.create(
                title='Book 3'
            ),
        ]

    def test_show_page_if_result_list_is_empty(self):
        """Bookモデル一覧画面への画面遷移（検索結果が0件）

        画面項目の確認
        - Bookモデル一覧画面に遷移できることを検証する
        - 検索結果一覧の表示内容を検証する
        - 合計件数メッセージが「全 X 件」と表示されていることを検証する
        - 追加ボタンが表示されることを検証する"""

        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)
        # Bookモデル一覧画面に遷移
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')

        # 画面表示項目を検証
        page = ChangeListPage(response.rendered_content)
        # 追加ボタンが表示されていること
        self.assertIsNotNone(page.add_button)
        # 簡易検索フォームが表示されていること
        self.assertIsNotNone(page.search_form)
        # 絞り込み（フィルタ）が表示されていること
        self.assertIsNotNone(page.filter)
        # アクション一覧が表示されていないこと
        self.assertIsNone(page.action_list)
        # 検索結果表示テーブルが表示されていないこと
        self.assertIsNone(page.result_list)

    def test_show_page_if_result_list_is_not_empty(self):
        """Bookモデル一覧画面への画面遷移（検索結果が0件でない）"""
        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # Bookモデル一覧画面に遷移
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')

        # 画面表示項目を検証
        page = ChangeListPage(response.rendered_content)
        # 追加ボタンが表示されていること
        self.assertIsNotNone(page.add_button)
        # 簡易検索フォームが表示されていること
        self.assertIsNotNone(page.search_form)
        # 絞り込み（フィルタ）が表示されていること
        self.assertIsNotNone(page.filter)
        # アクション一覧
        self.assertEqual(
            page.action_list_texts, ['---------', '選択された 本 の削除'])
        # 検索結果表示テーブル
        self.assertEqual(
            page.result_list_head_texts,
            ['ID', 'タイトル', '価格', 'サイズ', '出版日']
        )
        self.assertEqual(len(page.result_list_rows_texts), 3)
        self.assertEqual(
            page.result_list_rows_texts[0],
            ['Book 1', '1,000 円', 'A4 - 210 x 297 mm', '2020年1月1日']
        )
        self.assertEqual(
            page.result_list_rows_texts[1],
            ['Book 2', '2,000 円', 'B5 - 182 x 257 mm', '2020年2月1日']
        )
        self.assertEqual(
            page.result_list_rows_texts[2],
            ['Book 3', '-', '-', '-']
        )
        # 合計件数表示
        self.assertEqual(page.result_count_text, '全 3 件')

    def test_search(self):
        """Bookモデル一覧画面で簡易検索"""
        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # Bookモデル一覧画面で簡易検索を実行
        # タイトルで検索できること
        response = self.client.get(self.TARGET_URL + '?q=Book')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')
        self.assertEqual(response.context_data['cl'].result_count, 3)

        # 価格で検索できること
        response = self.client.get(self.TARGET_URL + '?q=100')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')
        self.assertEqual(response.context_data['cl'].result_count, 1)

    def test_filter_by_size(self):
        """Bookモデル一覧画面でサイズで絞り込む"""
        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # Bookモデル一覧画面で簡易検索を実行
        response = self.client.get(self.TARGET_URL + '?size__exact=a4')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')
        self.assertEqual(response.context_data['cl'].result_count, 1)

    def test_filter_by_prices(self):
        """Bookモデル一覧画面で価格で絞り込む"""
        # テストデータを作成
        self.create_books()
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # Bookモデル一覧画面で簡易検索を実行
        response = self.client.get(self.TARGET_URL + '?prices=1000%2C2000')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')
        self.assertEqual(response.context_data['cl'].result_count, 1)

    # ...（略）...


class TestAdminBookChangeListByViewStaff(TestCase):
    """管理サイトのBookモデル一覧画面のテスト（閲覧専用スタッフの場合）"""

    TARGET_URL = reverse('admin:shop_book_changelist')
    PASSWORD = 'pass12345'

    def setUp(self):
        # テストユーザー（閲覧専用スタッフ）を作成
        self.user = User.objects.create_user(
            'view_only_staff', 'view_only_staff@example.com', self.PASSWORD,
            is_staff=True)
        self.user.user_permissions.set(
            Permission.objects.filter(codename='view_book'))

        # テストデータを作成
        self.books = [
            Book.objects.create(
                title='Book 1',
                price=1000,
                size='a4',
                publish_date=datetime(2020, 1, 1)
            ),
        ]

    def test_page_items(self):
        """Bookモデル一覧画面への画面遷移

        - 追加ボタンが表示されないことを検証する"""
        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)

        # Bookモデル一覧画面に遷移
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
        # アクション一覧が表示されていないこと
        self.assertIsNone(page.action_list)
        # 検索結果表示テーブルが表示されていること
        self.assertIsNotNone(page.result_list)

    # ...（略）...


class TestAdminBookChangeListByAnonymousUser(TestCase):
    """管理サイトのBookモデル一覧画面のテスト（未ログインユーザーの場合）"""

    TARGET_URL = reverse('admin:shop_book_changelist')

    def test_get_change_list(self):
        """Bookモデル一覧画面への画面遷移

        - ログイン画面にリダイレクトされることを検証する"""
        # Bookモデル一覧画面に遷移（リダイレクトをともなう場合は follow=True を指定）
        response = self.client.get(self.TARGET_URL, follow=True)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/login.html')
