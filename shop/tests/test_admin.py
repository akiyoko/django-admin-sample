from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse_lazy

from ..models import Book, Author, Publisher

User = get_user_model()


class TestBookChangeListView(TestCase):
    """Book一覧画面のテストクラス"""

    TARGET_URL = reverse_lazy('admin:shop_book_changelist')  # '/admin/shop/book/'
    PASSWORD = 'pass12345'

    def setUp(self):
        # テストユーザーを作成
        self.superuser = User.objects.create_superuser(
            'admin', 'admin@example.com', self.PASSWORD)
        self.view_only_staff = User.objects.create_user(
            'view_only_staff', 'view_only_staff@example.com', self.PASSWORD, is_staff=True)
        self.view_only_staff.user_permissions.set(Permission.objects.filter(codename='view_book'))

        # モデルレコードを作成
        self.publisher = Publisher.objects.create(name='Publisher 1')
        self.author = Author.objects.create(name='Author 1')
        # self.books = Book.objects.bulk_create([
        #     # It does not work with many-to-many relationships.
        #     # See. https://docs.djangoproject.com/ja/2.2/ref/models/querysets/#bulk-create
        #     # ↓のエラーが発生
        #     # TypeError: Direct assignment to the forward side of a many-to-many set is prohibited. Use authors.set() instead.
        #     # Book(title='Book 1', price=1000, publisher=self.publisher, authors=[self.author]),
        #     Book(title='Book 1', price=1000, publisher=self.publisher),
        #     Book(title='Book 2', price=2000),
        # ])
        self.books = [
            Book.objects.create(
                title='Book %s' % (i + 1),
                price=(i + 1) * 1000,
                publisher=self.publisher,
                # authors=[self.author],  Use authors.set() instead.
            ) for i in range(2)
        ]

    def test_change_list_by_no_login_user(self):
        response = self.client.get(self.TARGET_URL)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/admin/login/?next=/admin/shop/book/')

    def test_change_list_by_view_only_staff(self):
        self.client.login(username=self.view_only_staff.username, password=self.PASSWORD)
        response = self.client.get(self.TARGET_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')

    def test_change_list_by_admin(self):
        self.client.login(username=self.superuser.username, password=self.PASSWORD)
        response = self.client.get(self.TARGET_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_list.html')
        self.assertEqual(response.context_data['cl'].result_count, 2)
        # Note: response.context_data['cl'].result_list に QuerySet がセットされているが、
        #       どこまでチェックするべき？
        self.assertListEqual(
            response.context_data['cl'].list_display,
            # 0番目の action_checkbox はチェックボックス
            [
                'action_checkbox', 'id', 'title', 'price', 'size', 'publish_date',
            ]
        )

    # def test_change_list_if_change_list_is_empty(self):
    #     self.client.login(username=self.superuser.username, password=self.PASSWORD)
    #     response = self.client.get(self.TARGET_URL)
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'admin/change_list.html')
    #     self.assertContains(response, "0 本")
    #
    # # TODO
    # def test_change_list_if_change_list_is_not_empty(self):
    #     application = Book.objects.create(title='aaa')
    #
    #     self.client.login(username=self.superuser.username, password=self.PASSWORD)
    #     response = self.client.get(self.TARGET_URL)
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'admin/change_list.html')
    #     # TODO: 表示項目を assert したい
    #     self.assertContains(response, "1 本")
