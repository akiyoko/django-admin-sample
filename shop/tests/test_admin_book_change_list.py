from datetime import datetime

import lxml.html
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from shop.models import Book
from .helpers import TestAdminChangeListMixin

User = get_user_model()


class TestAdminBookChangeList(TestAdminChangeListMixin, TestCase):
    """管理サイトのBookモデル一覧画面のユニットテスト（システム管理者の場合）"""

    TARGET_URL = reverse('admin:shop_book_changelist')
    PASSWORD = 'pass12345'

    def setUp(self):
        # テストユーザー（システム管理者）を作成
        self.user = User.objects.create_superuser(
            'admin', 'admin@example.com', self.PASSWORD)

        # テストレコードを作成
        self.books = [
            Book.objects.create(title='Book 1', price=1000, size='a4'),
            Book.objects.create(title='Book 2', publish_date=datetime(2020, 3, 1)),
        ]

    def test_get_change_list(self):
        """Bookモデル一覧画面への画面遷移（システム管理者の場合）

        1) Bookモデル一覧画面に遷移できることを検証する
        2) 検索結果一覧の表示内容を検証する
        3) 合計件数メッセージが「全 X 件」と表示されていることを検証する
        4) 追加ボタンが表示されることを検証する"""

        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)
        # Bookのモデル一覧画面に遷移
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')
        self.assertEqual(response.context_data['cl'].result_count, 2)

        # 画面表示項目を検証
        html = lxml.html.fromstring(response.rendered_content)
        # 検索結果一覧
        head, rows = self.get_result_list(html)
        self.assert_thead(head, ['ID', 'タイトル', '価格', 'サイズ', '出版日'])
        self.assertEqual(len(rows), 2)
        self.assert_tbody_row(
            rows[0], ['Book 1', '1,000 円', 'A4 - 210 x 297 mm', '-'])
        self.assert_tbody_row(
            rows[1], ['Book 2', '-', '-', '2020年3月1日'])
        # 合計件数メッセージ
        self.assert_result_count_message(html, '全 2 件')
        # アクション一覧
        self.assert_actions(html, ['---------', '選択された 本 の削除'])
        # 追加ボタン
        self.assert_link_is_displayed(html, 'addlink')

    def test_get_change_list_if_no_result(self):
        """Bookモデルのモデル一覧画面で検索結果が0件（システム管理者の場合）
        """
        # テストデータを削除しておく
        for book in self.books:
            book.delete()

        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)
        # Bookのモデル一覧画面に遷移
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')
        self.assertEqual(response.context_data['cl'].result_count, 0)

        # 画面表示項目を検証
        html = lxml.html.fromstring(response.rendered_content)
        # 検索結果一覧
        head, rows = self.get_result_list(html)
        self.assertEqual(head, None)
        self.assertEqual(len(rows), 0)

    def test_search_change_list(self):
        """Bookモデル一覧画面で簡易検索

        1) 簡易検索ができることを検証する"""

        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)
        # Bookのモデル一覧画面で簡易検索を実行
        response = self.client.get(self.TARGET_URL + '?q=1000')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')
        self.assertEqual(response.context_data['cl'].result_count, 1)

    # ...（略）...


class TestAdminBookChangeListByStaff(TestAdminChangeListMixin, TestCase):
    """管理サイトのBookモデル一覧画面のユニットテスト（閲覧スタッフの場合）"""

    TARGET_URL = reverse('admin:shop_book_changelist')
    PASSWORD = 'pass12345'

    def setUp(self):
        # テストユーザー（閲覧スタッフ）を作成
        self.user = User.objects.create_user(
            'view_only_staff', 'view_only_staff@example.com', self.PASSWORD,
            is_staff=True)
        self.user.user_permissions.set(
            Permission.objects.filter(codename='view_book'))

        # テストレコードを作成
        self.books = [
            Book.objects.create(title='Book 1', price=1000, size='a4'),
            Book.objects.create(title='Book 2', publish_date=datetime(2020, 3, 1)),
        ]

    def test_get_change_list(self):
        """Bookモデル一覧画面への画面遷移（閲覧用スタッフの場合）

        1) 閲覧用スタッフの場合、追加ボタンが表示されないことを検証する"""

        # ログイン
        self.client.login(username=self.user.username, password=self.PASSWORD)
        # Bookのモデル一覧画面に遷移
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')

        # 追加ボタンが表示されていないことを検証
        html = lxml.html.fromstring(response.rendered_content)
        self.assert_link_is_not_displayed(html, 'addlink')

    # ...（略）...


class TestAdminBookChangeListByNoLoginUser(TestAdminChangeListMixin, TestCase):
    """管理サイトのBookモデル一覧画面のユニットテスト（未ログインの場合）"""

    TARGET_URL = reverse('admin:shop_book_changelist')

    def setUp(self):
        # テストレコードを作成
        self.books = [
            Book.objects.create(title='Book 1', price=1000, size='a4'),
            Book.objects.create(title='Book 2', publish_date=datetime(2020, 3, 1)),
        ]

    def test_get_change_list(self):
        """Bookモデル一覧画面への画面遷移（未ログインの場合）

        1) 未ログインの場合、ログイン画面にリダイレクトされることを検証する"""

        # Bookのモデル一覧画面に遷移（リダイレクトをともなう場合は follow=True を指定）
        response = self.client.get(self.TARGET_URL, follow=True)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/login.html')

    # ...（略）...
