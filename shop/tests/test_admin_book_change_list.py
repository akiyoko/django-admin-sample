from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from ..models import Book

User = get_user_model()


class TestAdminBookChangeListView(TestCase):
    """管理サイト Bookモデル一覧画面のユニットテスト"""

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

        # モデルレコードを作成
        self.books = [
            Book.objects.create(
                title='Book {}'.format(i + 1),
                price=(i + 1) * 1000,
            ) for i in range(2)
        ]

    def test_change_list_by_admin(self):
        # システム管理者でログイン
        self.client.login(username=self.superuser.username, password=self.PASSWORD)
        # Bookのモデル一覧画面に遷移
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')
        self.assertEqual(response.context_data['cl'].result_count, 2)
        self.assertListEqual(
            response.context_data['cl'].list_display,
            # action_checkboxの0番目はチェックボックス
            [
                'action_checkbox', 'id', 'title', 'price', 'size', 'publish_date',
            ]
        )

    def test_change_list_by_view_only_staff(self):
        # 閲覧用スタッフでログイン
        self.client.login(
            username=self.view_only_staff.username, password=self.PASSWORD)
        # Bookのモデル一覧画面に遷移
        response = self.client.get(self.TARGET_URL)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')

    def test_change_list_by_no_login_user(self):
        # ログインせずにBookのモデル一覧画面に遷移
        response = self.client.get(self.TARGET_URL, follow=True)
        # レスポンスを検証
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/login.html')
