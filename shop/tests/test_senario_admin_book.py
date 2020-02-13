import os

from django.contrib.admin.tests import AdminSeleniumTestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from selenium import webdriver

try:
    # chromedriver-binaryのパスを通してくれる
    import chromedriver_binary
except ImportError:
    raise

from ..models import Book

User = get_user_model()


class TestSeleniumAdminBookChangeList(AdminSeleniumTestCase):
    """管理サイト Bookモデル一覧画面のシナリオテスト"""

    # スクリーンショットを保存するディレクトリ
    SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'screenshots')
    TARGET_URL = reverse('admin:shop_book_changelist')
    PASSWORD = 'secret'

    available_apps = None
    browser = 'chrome'

    @classmethod
    def create_webdriver(cls):
        """Chrome用のWebDriverインスタンスを作成する

        SeleniumTestCaseのsetUpClassで呼ばれるメソッドをオーバーライド"""
        chrome_options = webdriver.ChromeOptions()
        # ヘッドレスモード
        chrome_options.add_argument('--headless')
        return webdriver.Chrome(chrome_options=chrome_options)

    def setUp(self):
        super().setUp()
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
            Book.objects.create(
                title='Book {}'.format(i + 1),
                price=(i + 1) * 1000,
            ) for i in range(2)
        ]

    def tearDown(self):
        # スクリーンショットを撮る
        self.save_screenshot()
        super().tearDown()

    def test_book_change_list_by_admin(self):
        """Bookモデル一覧画面の画面表示の検証（システム管理者の場合）"""

        # システム管理者でログイン
        self.admin_login(self.superuser.username, self.PASSWORD)
        # Bookモデル一覧画面を表示
        self.selenium.get(self.live_server_url + self.TARGET_URL)
        self.wait_page_loaded()

        # # 検索結果一覧を検証
        # head, rows = self.get_result_list()
        # self.assert_thead(head, ['ID', 'タイトル', '価格', 'サイズ', '出版日'])
        # self.assertEqual(len(rows), 2)
        # self.assert_tbody_row(rows[0], ['Book 1', '1000', '-', '-'])
        # self.assert_tbody_row(rows[1], ['Book 2', '2000', '-', '-'])
        # # 件数表示を検証
        # self.assertIn(
        #     '全 2 件',
        #     self.selenium.find_element_by_xpath(
        #         '//form[@id="changelist-form"]/p[@class="paginator"]').text,
        # )

        # 追加ボタンが表示されていること
        self.assert_link_is_displayed('addlink')

    def test_book_change_list_by_view_only_staff(self):
        """Bookモデル一覧画面の画面表示の検証（閲覧用スタッフの場合）"""

        # 閲覧用スタッフでログイン
        self.admin_login(self.view_only_staff.username, self.PASSWORD)
        # Bookモデル一覧画面を表示
        self.selenium.get(self.live_server_url + self.TARGET_URL)
        self.wait_page_loaded()

        # # 検索結果一覧を検証
        # head, rows = self.get_result_list()
        # self.assert_thead(head, ['ID', 'タイトル', '価格', 'サイズ', '出版日'])
        # self.assertEqual(len(rows), 2)
        # self.assert_tbody_row(rows[0], ['Book 1', '1000', '-', '-'])
        # self.assert_tbody_row(rows[1], ['Book 2', '2000', '-', '-'])

        # 追加ボタンが表示されていないこと
        self.assert_link_is_not_displayed('addlink')

    def save_screenshot(self):
        """スクリーンショットを撮る"""
        if not os.path.exists(self.SCREENSHOT_DIR):
            os.makedirs(self.SCREENSHOT_DIR, exist_ok=True)
        filename = '{}.png'.format(self.id())
        i = 0
        while os.path.exists(os.path.join(self.SCREENSHOT_DIR, filename)):
            i += 1
            filename = '{}_{}.png'.format(self.id(), i)
        self.selenium.save_screenshot(os.path.join(self.SCREENSHOT_DIR, filename))

    # def get_result_list(self):
    #     """検索結果テーブルの要素を取得する"""
    #     table = self.selenium.find_element_by_id('result_list')
    #     head = table.find_element_by_xpath('thead/tr')
    #     rows = table.find_elements_by_xpath('tbody/tr')
    #     return head, rows
    #
    # def assert_thead(self, head, expected_texts):
    #     """検索結果テーブルのヘッダを検証する"""
    #     head_texts = [c.text for c in head.find_elements_by_xpath(
    #         'th[contains(@class, "column-")]')]
    #     self.assertListEqual(head_texts, expected_texts)
    #
    # def assert_tbody_row(self, row, expected_texts):
    #     """検索結果テーブルのレコード行を検証する"""
    #     row_texts = [f.text for f in row.find_elements_by_xpath(
    #         'td[contains(@class, "field-")]')]
    #     self.assertListEqual(row_texts, expected_texts)
    #
    # def assert_link_is_displayed(self, css_class):
    #     """リンクが表示されていることを検証する"""
    #     self.assertTrue(self.selenium.find_element_by_xpath(
    #         '//a[@class="{}"]'.format(css_class)).is_displayed())
    #
    # def assert_link_is_not_displayed(self, css_class):
    #     """リンクが表示されていないことを検証する"""
    #     self.assertTrue(
    #         len(self.selenium.find_elements_by_xpath(
    #             '//a[@class="{}"]'.format(css_class))) == 0)
