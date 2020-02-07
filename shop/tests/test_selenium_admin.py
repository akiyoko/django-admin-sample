import os

from django.contrib.admin.tests import AdminSeleniumTestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
#from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse
from selenium import webdriver

try:
    import chromedriver_binary
except ImportError:
    raise

from ..models import Book

User = get_user_model()


@tag('selenium')
class TestAdminListDisplay(AdminSeleniumTestCase):
    """管理サイト: モデル一覧画面のシナリオテスト

    https://chromedriver.chromium.org/downloads
    https://github.com/danielkaiser/python-chromedriver-binary/releases
    を確認し、Chromeのバージョンに合わせてchromedriver-binaryをインストールする。
    例えば、Chromeのバージョンが80であれば、pip install chromedriver-binary==80.0.3987.16.0
    """
    SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshots')
    PASSWORD = 'secret'

    available_apps = None
    # browsers = ['chrome']
    browser = 'chrome'

    @classmethod
    def create_webdriver(cls):
        chrome_options = webdriver.ChromeOptions()
        # headlessモード
        chrome_options.add_argument('--headless')
        return webdriver.Chrome(chrome_options=chrome_options)

    @classmethod
    def setUpClass(cls):
        # 案1: headlessモードじゃない selenium が起動してしまうので、
        #      django.test.selenium.SeleniumTestCase の setUpClass は呼ばないようにする。
        #      もし super().setUpClass() を呼んでしまうと、二重に起動してしまう。
        # super(StaticLiveServerTestCase, cls).setUpClass()
        # chrome_options = webdriver.ChromeOptions()
        # # headlessモード
        # chrome_options.add_argument('--headless')
        # cls.selenium = webdriver.Chrome(chrome_options=chrome_options)
        # cls.selenium.implicitly_wait(5)

        # 案2: create_webdriver() をオーバーライドして Chrome の WebDriverインスタンスを返すようにする
        super().setUpClass()

    def setUp(self):
        super().setUp()
        # テストユーザーを作成
        self.superuser = User.objects.create_superuser(
            username='admin', email='admin@example.com', password=self.PASSWORD)
        self.view_only_staff = User.objects.create_user(
            'view_only_staff', 'view_only_staff@example.com', self.PASSWORD, is_staff=True)
        self.view_only_staff.user_permissions.set(Permission.objects.filter(codename='view_book'))

        # モデルレコードを作成
        self.books = [
            Book.objects.create(title='Book %s' % (i + 1), price=(i + 1) * 1000) for i in range(2)
        ]
        # self.book1 = Book.objects.create(title='Book 1', price=1000)
        # self.book2 = Book.objects.create(title='Book 2', price=2000)

    def tearDown(self):
        # スクリーンショットを撮る
        self.save_screenshot()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        # Note: ChromeDriverをheadlessモードで利用する場合、
        #       tearDownClassでcls.selenium.quit()を実行すると、
        #       「ConnectionResetError: [WinError 10054] 既存の接続はリモート ホストに強制的に切断されました。」
        #       というエラーが頻繁に発生してしまう
        # cls.selenium.quit()
        super().tearDownClass()

    def save_screenshot(self):
        """スクリーンショットを撮る"""
        if not os.path.exists(self.SCREENSHOT_DIR):
            os.makedirs(self.SCREENSHOT_DIR, exist_ok=True)
        screenshot_path = os.path.join(self.SCREENSHOT_DIR, '{}.png'.format(self.id()))
        self.selenium.save_screenshot(screenshot_path)

    def get_result_list(self):
        """検索結果テーブルの要素を取得する"""
        table = self.selenium.find_element_by_id('result_list')
        head = table.find_element_by_xpath('thead/tr')
        rows = table.find_elements_by_xpath('tbody/tr')
        return head, rows

    def assert_thead(self, head, expected_texts):
        """検索結果テーブルのヘッダを検証する"""
        head_texts = [c.text for c in
                      head.find_elements_by_xpath('th[contains(@class, "column-")]')]
        self.assertListEqual(head_texts, expected_texts)

    def assert_tbody_row(self, row, expected_texts):
        """検索結果テーブルのレコード行を検証する"""
        row_texts = [f.text for f in row.find_elements_by_xpath('td[contains(@class, "field-")]')]
        self.assertListEqual(row_texts, expected_texts)

    def assert_link_is_displayed(self, css_class):
        self.assertTrue(self.selenium.find_element_by_xpath(
            '//a[@class="{}"]'.format(css_class)).is_displayed())

    def assert_link_is_not_displayed(self, css_class):
        self.assertTrue(
            len(self.selenium.find_elements_by_xpath('//a[@class="{}"]'.format(css_class))) == 0)

    def test_book_changelist(self):
        """Bookモデル一覧画面の検証（システム管理者の場合）"""
        # システム管理者でログイン
        self.admin_login(self.superuser.username, self.PASSWORD)
        # Bookモデル一覧画面を表示
        self.selenium.get(self.live_server_url + reverse('admin:shop_book_changelist'))
        self.wait_page_loaded()

        # 検索結果一覧を検証
        head, rows = self.get_result_list()
        self.assert_thead(head, ['ID', 'タイトル', '価格', 'サイズ', '出版日'])
        self.assertEqual(len(rows), 2)
        self.assert_tbody_row(rows[0], ['Book 1', '1000', '-', '-'])
        self.assert_tbody_row(rows[1], ['Book 2', '2000', '-', '-'])

        # 追加ボタンが表示されていること
        self.assert_link_is_displayed('addlink')

    def test_book_changelist_by_view_only_staff(self):
        """Bookモデル一覧画面の検証（参照権限スタッフの場合）"""
        # 参照権限のみのスタッフでログイン
        self.admin_login(self.view_only_staff.username, self.PASSWORD)
        # Bookモデル一覧画面を表示
        self.selenium.get(self.live_server_url + reverse('admin:shop_book_changelist'))
        self.wait_page_loaded()

        # 検索結果一覧を検証
        head, rows = self.get_result_list()
        self.assert_thead(head, ['ID', 'タイトル', '価格', 'サイズ', '出版日'])
        self.assertEqual(len(rows), 2)
        self.assert_tbody_row(rows[0], ['Book 1', '1000', '-', '-'])
        self.assert_tbody_row(rows[1], ['Book 2', '2000', '-', '-'])

        # 追加ボタンが表示されていないこと
        self.assert_link_is_not_displayed('addlink')
