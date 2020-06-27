import os
from glob import glob

from django.contrib.admin.tests import AdminSeleniumTestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from selenium import webdriver

try:
    # importすることでChromeDriverのパスを通してくれる
    import chromedriver_binary
except ImportError:
    raise

from shop.models import Book

User = get_user_model()


class TestAdminSenario(AdminSeleniumTestCase):
    """管理サイトのシナリオテスト"""

    # スクリーンショットを保存するディレクトリ
    SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'screenshots')
    PASSWORD = 'secret'

    available_apps = None
    browser = 'chrome'

    @classmethod
    def create_webdriver(cls):
        """Chrome用のWebDriverインスタンスを作成する"""
        chrome_options = webdriver.ChromeOptions()
        # ヘッドレスモード
        chrome_options.add_argument('--headless')
        return webdriver.Chrome(chrome_options=chrome_options)

    def setUp(self):
        super().setUp()
        # 前回のスクリーンショットを削除しておく
        self.cleanup_screenshots()

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

    def test_book_crud(self):
        """BookモデルのCRUD検証（システム管理者の場合）"""

        # 1) ログイン画面に遷移
        self.selenium.get(self.live_server_url + '/admin/')
        self.wait_page_loaded()
        self.assert_title('ログイン')
        # スクリーンショットを撮る
        self.save_screenshot()

        # 2) システム管理者でログイン
        #    -> ホーム画面に遷移
        self.admin_login(self.superuser.username, self.PASSWORD)
        self.assert_title('サイト管理')
        # スクリーンショットを撮る
        self.save_screenshot()

        # 3) ホーム画面で「ショップ」リンクを押下
        #    -> アプリケーションホーム画面に遷移
        self.selenium.find_element_by_link_text('ショップ').click()
        self.wait_page_loaded()
        self.assert_title('ショップ 管理')
        # スクリーンショットを撮る
        self.save_screenshot()

        # 4) アプリケーションホーム画面で「本」リンクを押下
        #    -> Bookモデル一覧画面に遷移
        self.selenium.find_element_by_link_text('本').click()
        self.wait_page_loaded()
        self.assert_title('変更する 本 を選択')
        _, rows = self.get_result_list()
        self.assertEqual(len(rows), 0)
        # スクリーンショットを撮る
        self.save_screenshot()

        # 5) Bookモデル一覧画面で「本 を追加」リンクを押下
        #    -> Bookモデル追加画面に遷移
        self.selenium.find_element_by_link_text('本 を追加').click()
        self.wait_page_loaded()
        self.assert_title('本 を追加')
        # スクリーンショットを撮る
        self.save_screenshot()

        # 6) Bookモデル追加画面で入力内容を変更して「保存」ボタンを押下
        #    -> Bookモデル一覧画面に遷移
        self.selenium.find_element_by_name('title').send_keys('Book 1')
        self.selenium.find_element_by_name('price').send_keys('1000')
        self.selenium.find_element_by_xpath(
            '//select[@name="size"]/option[text()="%s"]' % 'A4 - 210 x 297 mm'
        ).click()
        self.selenium.find_element_by_name('publish_date').send_keys('2020-03-01')
        self.selenium.find_element_by_xpath(
            '//input[@value="%s"]' % '保存').click()
        self.wait_page_loaded()
        self.assert_title('変更する 本 を選択')
        _, rows = self.get_result_list()
        self.assertEqual(len(rows), 1)
        # スクリーンショットを撮る
        self.save_screenshot()

        # 7) Bookモデル一覧画面で追加した本のタイトルリンクを押下
        #    -> Bookモデル変更画面に遷移
        _, rows = self.get_result_list()
        rows[0].find_element_by_link_text('Book 1').click()
        self.wait_page_loaded()
        self.assert_title('本 を変更')
        # スクリーンショットを撮る
        self.save_screenshot()

        # 8) Bookモデル変更画面で「保存」ボタンを押下
        #    -> Bookモデル一覧画面に遷移
        self.selenium.find_element_by_name('price').clear()
        self.selenium.find_element_by_name('price').send_keys('2000')
        self.selenium.find_element_by_xpath(
            '//input[@value="%s"]' % '保存').click()
        self.wait_page_loaded()
        self.assert_title('変更する 本 を選択')
        _, rows = self.get_result_list()
        self.assertEqual(len(rows), 1)
        # レコードが更新されていることを検証
        book = Book.objects.get(title='Book 1')
        self.assertEqual(book.price, 2000)
        # スクリーンショットを撮る
        self.save_screenshot()

    def test_book_crud_by_view_only_staff(self):
        """BookモデルのCRUD検証（閲覧用スタッフの場合）"""

        # 1) ログイン画面に遷移
        self.selenium.get(self.live_server_url + '/admin/')
        self.wait_page_loaded()
        self.assert_title('ログイン')
        # スクリーンショットを撮る
        self.save_screenshot()

        # 2) 閲覧用スタッフでログイン
        #    -> ホーム画面に遷移
        self.admin_login(self.view_only_staff.username, self.PASSWORD)
        self.assert_title('サイト管理')
        # スクリーンショットを撮る
        self.save_screenshot()

        # 3) ホーム画面で「ショップ」リンクを押下
        #    -> アプリケーションホーム画面に遷移
        self.selenium.find_element_by_link_text('ショップ').click()
        self.wait_page_loaded()
        self.assert_title('ショップ 管理')
        # スクリーンショットを撮る
        self.save_screenshot()

        # 4) アプリケーションホーム画面で「本」リンクを押下
        #    -> Bookモデル一覧画面に遷移
        self.selenium.find_element_by_link_text('本').click()
        self.wait_page_loaded()
        self.assert_title('表示する本を選択')
        # 「本 を追加」リンクが表示されていないことを検証
        self.assertTrue(
            len(self.selenium.find_elements_by_link_text('本 を追加')) == 0)
        # スクリーンショットを撮る
        self.save_screenshot()

    def save_screenshot(self):
        """スクリーンショットを撮る

        ファイル名は「テストID + (連番).png」
        例)
        - shop.tests.test_admin_senario.TestAdminSenario.test_book_crud.png
        - shop.tests.test_admin_senario.TestAdminSenario.test_book_crud (1).png
        - shop.tests.test_admin_senario.TestAdminSenario.test_book_crud (2).png
        """
        if not os.path.exists(self.SCREENSHOT_DIR):
            os.makedirs(self.SCREENSHOT_DIR, exist_ok=True)

        filename = '{}.png'.format(self.id())
        i = 0
        while os.path.exists(os.path.join(self.SCREENSHOT_DIR, filename)):
            i += 1
            filename = '{} ({}).png'.format(self.id(), i)
        self.selenium.save_screenshot(os.path.join(self.SCREENSHOT_DIR, filename))

    def cleanup_screenshots(self):
        """ファイル名が「テストID + (連番).png」のスクリーンショットを削除する"""
        for f in glob('{}/{}.png'.format(self.SCREENSHOT_DIR, self.id())):
            os.remove(f)
        for f in glob('{}/{} ([0-9]*).png'.format(self.SCREENSHOT_DIR, self.id())):
            os.remove(f)

    def get_result_list(self):
        """検索結果テーブルの要素を取得する"""
        if not self.selenium.find_elements_by_id('result_list'):
            return None, []
        table = self.selenium.find_element_by_id('result_list')
        head = table.find_element_by_xpath('thead/tr')
        rows = table.find_elements_by_xpath('tbody/tr')
        return head, rows

    def assert_title(self, text):
        """タイトルを検証する"""
        self.assertEqual(self.selenium.title.split(' | ')[0], text)
