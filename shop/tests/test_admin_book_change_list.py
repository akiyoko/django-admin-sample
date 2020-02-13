from datetime import datetime

import lxml.html
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from shop.models import Book

User = get_user_model()


class TestAdminBookChangeList(TestCase):
    """Bookモデル一覧画面のユニットテスト"""

    TARGET_URL = reverse('admin:shop_book_changelist')
    PASSWORD = 'pass12345'

    def setUp(self):
        # テストユーザーを作成
        # システム管理者
        self.superuser = User.objects.create_superuser(
            'admin', 'admin@example.com', self.PASSWORD)
        # 閲覧用スタッフ
        self.view_only_staff = User.objects.create_user(
            'view_only_staff', 'view_only_staff@example.com', self.PASSWORD,
            is_staff=True)
        self.view_only_staff.user_permissions.set(
            Permission.objects.filter(codename='view_book'))

        # テストレコードを作成
        self.books = [
            Book.objects.create(title='Book 1', price=1000, size='a4'),
            Book.objects.create(title='Book 2', publish_date=datetime(2020, 3, 1)),
        ]

    def test_get_change_list(self):
        """Bookモデル一覧画面への画面遷移（システム管理者の場合）

        - 検索結果一覧の表示内容を検証する
        - 合計件数の表示メッセージが「全 X 件」となっていることを検証する
        - 追加ボタンが表示されていることを検証する"""

        # システム管理者でログイン
        self.client.login(username=self.superuser.username, password=self.PASSWORD)
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
        self.assert_tbody_row(rows[0], ['Book 1', '1,000 円', 'A4 - 210 x 297 mm', '-'])
        self.assert_tbody_row(rows[1], ['Book 2', '-', '-', '2020年3月1日'])
        # 合計件数メッセージ
        self.assert_result_count_message(html, '全 2 件')
        # 追加ボタンが表示されていること
        self.assert_link_is_displayed(html, 'addlink')

    def test_get_change_list_by_view_only_staff(self):
        """Bookモデル一覧画面への画面遷移（閲覧用スタッフの場合）

        - 追加ボタンが表示されていないことを検証する"""

        # 閲覧用スタッフでログイン
        self.client.login(
            username=self.view_only_staff.username, password=self.PASSWORD)
        # Bookのモデル一覧画面に遷移
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')

        # 追加ボタンが表示されていないこと
        html = lxml.html.fromstring(response.rendered_content)
        self.assert_link_is_not_displayed(html, 'addlink')

    def test_get_change_list_by_no_login_user(self):
        """Bookモデル一覧画面への画面遷移（未ログインの場合）

        - ログイン画面にリダイレクトされることを検証する"""

        # Bookのモデル一覧画面に遷移（リダイレクトをともなう場合は follow=True を指定）
        response = self.client.get(self.TARGET_URL, follow=True)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/login.html')

    def test_search_change_list(self):
        """Bookモデル一覧画面で簡易検索

        - 簡易検索ができることを検証する"""

        # システム管理者でログイン
        self.client.login(username=self.superuser.username, password=self.PASSWORD)
        # Bookのモデル一覧画面で簡易検索を実行
        response = self.client.get(self.TARGET_URL + '?q=1000')
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')
        self.assertEqual(response.context_data['cl'].result_count, 1)

    # ...（略）...

    def get_result_list(self, html):
        """検索結果テーブルの要素を取得する"""
        table = html.xpath('//table[@id="result_list"]')[0]
        head = table.xpath('thead/tr')[0]
        rows = table.xpath('tbody/tr')
        return head, rows

    def assert_thead(self, head, expected_texts):
        """検索結果テーブルのヘッダを検証する"""
        head_texts = [
            e.text_content() for e in
            head.xpath('th[contains(@class, "column-")]/div[@class="text"]')
        ]
        self.assertListEqual(head_texts, expected_texts)

    def assert_tbody_row(self, row, expected_texts):
        """検索結果テーブルのレコード行を検証する"""
        row_texts = [
            e.text_content() for e in
            row.xpath('td[contains(@class, "field-")]')
        ]
        self.assertListEqual(row_texts, expected_texts)

    def assert_result_count_message(self, html, message):
        """合計件数のメッセージを検証する"""
        self.assertIn(message, html.xpath(
            '//form[@id="changelist-form"]/p[@class="paginator"]')[0].text)

    def assert_link_is_displayed(self, html, css_class):
        """リンクが表示されていることを検証する"""
        self.assertTrue(len(html.xpath('//a[@class="{}"]'.format(css_class))) == 1)

    def assert_link_is_not_displayed(self, html, css_class):
        """リンクが表示されていないことを検証する"""
        self.assertTrue(len(html.xpath('//a[@class="{}"]'.format(css_class))) == 0)
