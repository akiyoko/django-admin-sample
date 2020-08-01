import os
from datetime import date
from glob import glob

from django.contrib.admin.tests import AdminSeleniumTestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from selenium import webdriver

try:
    # chromedriver_binaryをimportすることでChromeDriverのパスを通してくれる
    import chromedriver_binary
except ImportError:
    raise

from ..models import Book

User = get_user_model()


class CustomAdminSeleniumTestCase(AdminSeleniumTestCase):
    """管理サイトのブラウザテスト用のTestCase"""

    # スクリーンショットを保存するディレクトリ
    SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'screenshots')
    # ウィンドウのデフォルトサイズ
    DEFAULT_WINDOW_WIDTH = 1000
    DEFAULT_WINDOW_HEIGHT = 750

    available_apps = None
    browser = 'chrome'

    def setUp(self):
        # 前回のスクリーンショットを削除しておく
        self.cleanup_screenshots()

    @classmethod
    def create_webdriver(cls):
        """Chrome用のWebDriverインスタンスを作成する"""
        chrome_options = webdriver.ChromeOptions()
        # ヘッドレスモード
        chrome_options.add_argument('--headless')
        # 言語設定
        chrome_options.add_argument('--lang=ja')
        # ウィンドウサイズ
        chrome_options.add_argument('--window-size={},{}'.format(
            cls.DEFAULT_WINDOW_WIDTH, cls.DEFAULT_WINDOW_HEIGHT))
        return webdriver.Chrome(chrome_options=chrome_options)

    def set_window_size(self, width=None, height=None):
        """ウィンドウサイズを変更する"""
        if width is None:
            width = self.DEFAULT_WINDOW_WIDTH
        if height is None:
            height = self.DEFAULT_WINDOW_HEIGHT
        self.selenium.set_window_size(width, height)

    def save_screenshot(self, width=None, height=None):
        """スクリーンショットを撮る

        ファイル名は「<テストID>_(<連番>).png」
        例)
        - shop.tests.test_admin_senario.TestAdminSenario.test_book_crud.png
        - shop.tests.test_admin_senario.TestAdminSenario.test_book_crud_(2).png
        - shop.tests.test_admin_senario.TestAdminSenario.test_book_crud_(3).png
        """
        if not os.path.exists(self.SCREENSHOT_DIR):
            os.makedirs(self.SCREENSHOT_DIR, exist_ok=True)

        # ウィンドウサイズを変更
        current_window_size = self.selenium.get_window_size()
        if width is not None or height is not None:
            self.set_window_size(width, height)

        filename = '{}.png'.format(self.id())
        i = 1
        while os.path.exists(os.path.join(self.SCREENSHOT_DIR, filename)):
            i += 1
            filename = '{}_({}).png'.format(self.id(), i)
        self.selenium.save_screenshot(os.path.join(self.SCREENSHOT_DIR, filename))

        # ウィンドウサイズを元に戻す
        self.set_window_size(
            current_window_size['width'], current_window_size['height'])

    def cleanup_screenshots(self):
        """過去のスクリーンショットを削除する"""
        # ファイル名が「<テストID>.png」のスクリーンショットを削除
        filename = '{}.png'.format(self.id())
        for f in glob(os.path.join(self.SCREENSHOT_DIR, filename)):
            os.remove(f)
        # ファイル名が「<テストID>_(<連番>).png」のスクリーンショットを削除
        filename = '{}_([0-9]*).png'.format(self.id())
        for f in glob(os.path.join(self.SCREENSHOT_DIR, filename)):
            os.remove(f)

    def assert_title(self, text):
        """タイトルを検証する"""
        self.assertEqual(self.selenium.title.split(' | ')[0], text)

    def select_option(self, name, text):
        """セレクトボックスを選択する"""
        self.selenium.find_element_by_xpath(
            '//select[@name="{}"]/option[text()="{}"]'.format(name, text)
        ).click()

    def get_result_list_rows(self):
        """検索結果表示テーブルのデータ行の要素オブジェクトを取得する"""
        result_list = self.selenium.find_elements_by_id('result_list')
        if len(result_list) == 0:
            return None
        return result_list[0].find_elements_by_xpath('tbody/tr')

    def get_action_list(self):
        """アクション一覧の要素オブジェクトを取得する"""
        changelist_form = self.selenium.find_elements_by_id('changelist-form')
        if len(changelist_form) == 0:
            return None
        return changelist_form[0].find_elements_by_xpath('//select/option')


class TestAdminSenario(CustomAdminSeleniumTestCase):
    """管理サイトのシナリオテスト（システム管理者の場合）"""

    PASSWORD = 'pass12345'

    def setUp(self):
        super().setUp()
        # テストユーザー（システム管理者）を作成
        self.user = User.objects.create_superuser(
            'admin', 'admin@example.com', self.PASSWORD)

    def test_book_crud(self):
        """BookモデルのCRUD検証（システム管理者の場合）"""

        # 1. ログイン画面に遷移
        self.selenium.get(self.live_server_url + '/admin/')
        self.wait_page_loaded()
        self.assert_title('ログイン')
        # スクリーンショットを撮る（1枚目）
        self.save_screenshot()

        # 2. システム管理者でログイン
        self.admin_login(self.user.username, self.PASSWORD)
        # ホーム画面が表示されていることを確認
        self.assert_title('ホーム')
        # スクリーンショットを撮る（2枚目）
        self.save_screenshot()

        # 3. ホーム画面で「ショップ」リンクを押下
        self.selenium.find_element_by_link_text('ショップ').click()
        self.wait_page_loaded()
        # アプリケーションホーム画面が表示されていることを確認
        self.assert_title('ショップ 管理')
        # スクリーンショットを撮る（3枚目）
        self.save_screenshot()

        # 4. アプリケーションホーム画面で「本」リンクを押下
        self.selenium.find_element_by_link_text('本').click()
        self.wait_page_loaded()
        # モデル一覧画面が表示されていることを確認
        self.assert_title('変更する 本 を選択')
        self.assertIsNone(self.get_result_list_rows())
        # スクリーンショットを撮る（4枚目）
        self.save_screenshot()

        # 5. モデル一覧画面で「本 を追加」ボタンを押下
        self.selenium.find_element_by_link_text('本 を追加').click()
        self.wait_page_loaded()
        # モデル追加画面が表示されていることを確認
        self.assert_title('本 を追加')
        # スクリーンショットを撮る（5枚目）
        self.save_screenshot(height=950)

        # 6. モデル追加画面で項目を入力して「保存」ボタンを押下
        self.selenium.find_element_by_name('title').send_keys('Book 1')
        self.selenium.find_element_by_name('price').send_keys('1000')
        self.select_option('size', 'A4 - 210 x 297 mm')
        self.selenium.find_element_by_name('publish_date').send_keys('2020-09-01')
        self.selenium.find_element_by_xpath(
            '//input[@value="{}"]'.format('保存')).click()
        self.wait_page_loaded()
        # モデル一覧画面が表示されていることを確認
        self.assert_title('変更する 本 を選択')
        self.assertEqual(len(self.get_result_list_rows()), 1)
        # レコードが追加されていることを確認
        self.assertTrue(Book.objects.filter(title='Book 1').exists())
        # スクリーンショットを撮る（6枚目）
        self.save_screenshot()

        # 7. モデル一覧画面で追加した本のリンクを押下
        rows = self.get_result_list_rows()
        rows[0].find_element_by_tag_name('a').click()
        self.wait_page_loaded()
        # モデル変更画面が表示されていることを確認
        self.assert_title('本 を変更')
        # スクリーンショットを撮る（7枚目）
        self.save_screenshot(height=950)

        # 8. モデル変更画面で項目を変更して「保存」ボタンを押下
        self.selenium.find_element_by_name('price').clear()
        self.selenium.find_element_by_name('price').send_keys('2000')
        self.selenium.find_element_by_xpath(
            '//input[@value="{}"]'.format('保存')).click()
        self.wait_page_loaded()
        # モデル一覧画面が表示されていることを確認
        self.assert_title('変更する 本 を選択')
        self.assertEqual(len(self.get_result_list_rows()), 1)
        # レコードが更新されていることを確認
        book = Book.objects.get(title='Book 1')
        self.assertEqual(book.price, 2000)
        # スクリーンショットを撮る（8枚目）
        self.save_screenshot()

        # 9. モデル一覧画面で追加した本のチェックボックスを選択し、
        #    アクション一覧から「選択された 本 の削除」を選択して「実行」ボタンを押下
        rows = self.get_result_list_rows()
        rows[0].find_element_by_xpath('//input[@type="checkbox"]').click()
        self.select_option('action', '選択された 本 の削除')
        self.selenium.find_element_by_xpath(
            '//form[@id="changelist-form"]//button[@type="submit"]').click()
        self.wait_page_loaded()
        # モデル削除確認画面が表示されていることを確認
        self.assert_title('よろしいですか？')
        # スクリーンショットを撮る（9枚目）
        self.save_screenshot()

        # 10. モデル削除確認画面で「はい」ボタンを押下
        self.selenium.find_element_by_xpath(
            '//input[@value="{}"]'.format('はい')).click()
        self.wait_page_loaded()
        # モデル一覧画面が表示されていることを確認
        self.assert_title('変更する 本 を選択')
        self.assertIsNone(self.get_result_list_rows())
        # レコードが削除されていることを確認
        self.assertFalse(Book.objects.filter(title='Book 1').exists())
        # スクリーンショットを撮る（10枚目）
        self.save_screenshot()


class TestAdminSenarioByViewStaff(CustomAdminSeleniumTestCase):
    """管理サイトのシナリオテスト（閲覧用スタッフの場合）"""

    PASSWORD = 'pass12345'

    def setUp(self):
        super().setUp()
        # テストユーザー（閲覧用スタッフ）を作成
        self.user = User.objects.create_user(
            'staff', 'staff@example.com', self.PASSWORD, is_staff=True)
        self.user.user_permissions.set(
            Permission.objects.filter(codename='view_book'))

        # テストレコードを作成
        self.book = Book.objects.create(
            title='Book 1',
            price=1000,
            size=Book.SIZE_A4,
            publish_date=date(2020, 1, 1),
        )

    def test_book_crud(self):
        """BookモデルのCRUD検証（閲覧用スタッフの場合）"""

        # 1. ログイン画面に遷移
        self.selenium.get(self.live_server_url + '/admin/')
        self.wait_page_loaded()
        self.assert_title('ログイン')
        # スクリーンショットを撮る（1枚目）
        self.save_screenshot()

        # 2. 閲覧用スタッフでログイン
        self.admin_login(self.user.username, self.PASSWORD)
        # ホーム画面が表示されていることを確認
        self.assert_title('ホーム')
        # スクリーンショットを撮る（2枚目）
        self.save_screenshot()

        # 3. ホーム画面で「ショップ」リンクを押下
        self.selenium.find_element_by_link_text('ショップ').click()
        self.wait_page_loaded()
        # アプリケーションホーム画面が表示されていることを確認
        self.assert_title('ショップ 管理')
        # スクリーンショットを撮る（3枚目）
        self.save_screenshot()

        # 4. アプリケーションホーム画面で「本」リンクを押下
        self.selenium.find_element_by_link_text('本').click()
        self.wait_page_loaded()
        # モデル一覧画面が表示されていることを確認
        self.assert_title('表示する本を選択')
        # 「本 を追加」ボタンが表示されていないことを確認
        self.assertTrue(
            len(self.selenium.find_elements_by_link_text('本 を追加')) == 0)
        # アクション一覧に一括削除が含まれていないことを確認
        self.assertNotIn(
            '選択された 本 の削除',
            [action.text for action in self.get_action_list()]
        )
        # スクリーンショットを撮る（4枚目）
        self.save_screenshot()
