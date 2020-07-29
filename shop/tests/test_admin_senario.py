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

from ..models import Book

User = get_user_model()


class CustomAdminSeleniumTestCase(AdminSeleniumTestCase):
    """管理サイトのシナリオテスト用のMixin"""

    # スクリーンショットを保存するディレクトリ
    SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'screenshots')

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
        return webdriver.Chrome(chrome_options=chrome_options)

    def save_screenshot(self):
        """スクリーンショットを撮る

        ファイル名は「<テストID>_(<2からの連番>).png」
        例)
        - shop.tests.test_admin_senario.TestAdminSenario.test_book_crud.png
        - shop.tests.test_admin_senario.TestAdminSenario.test_book_crud_(2).png
        - shop.tests.test_admin_senario.TestAdminSenario.test_book_crud_(3).png
        """
        if not os.path.exists(self.SCREENSHOT_DIR):
            os.makedirs(self.SCREENSHOT_DIR, exist_ok=True)

        filename = '{}.png'.format(self.id())
        i = 1
        while os.path.exists(os.path.join(self.SCREENSHOT_DIR, filename)):
            i += 1
            filename = '{}_({}).png'.format(self.id(), i)
        self.selenium.save_screenshot(os.path.join(self.SCREENSHOT_DIR, filename))

    def cleanup_screenshots(self):
        """過去のスクリーンショットを削除する"""
        # ファイル名が「<テストID>.png」のスクリーンショットを削除
        for f in glob('{}/{}.png'.format(self.SCREENSHOT_DIR, self.id())):
            os.remove(f)
        # ファイル名が「<テストID>_(<連番>).png」のスクリーンショットを削除
        for f in glob('{}/{}_([0-9]*).png'.format(self.SCREENSHOT_DIR, self.id())):
            os.remove(f)

    def assert_title(self, text):
        """タイトルを検証する"""
        self.assertEqual(self.selenium.title.split(' | ')[0], text)

    def get_result_list_rows(self):
        """検索結果テーブルの要素を取得する"""
        if not self.selenium.find_elements_by_id('result_list'):
            return None
        table = self.selenium.find_element_by_id('result_list')
        rows = table.find_elements_by_xpath('tbody/tr')
        return rows


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

        # 1) ログイン画面に遷移
        self.selenium.get(self.live_server_url + '/admin/')
        self.wait_page_loaded()
        self.assert_title('ログイン')
        # スクリーンショット（1枚目）を撮る
        self.save_screenshot()

        # 2) システム管理者でログイン
        self.admin_login(self.user.username, self.PASSWORD)
        # ホーム画面が表示されていることを確認
        self.assert_title('ホーム')
        # スクリーンショット（2枚目）を撮る
        self.save_screenshot()

        # 3) ホーム画面で「ショップ」リンクを押下
        self.selenium.find_element_by_link_text('ショップ').click()
        self.wait_page_loaded()
        # アプリケーションホーム画面が表示されていることを確認
        self.assert_title('ショップ 管理')
        # スクリーンショット（3枚目）を撮る
        self.save_screenshot()

        # 4) アプリケーションホーム画面で「本」リンクを押下
        self.selenium.find_element_by_link_text('本').click()
        self.wait_page_loaded()
        # Bookモデル一覧画面が表示されていることを確認
        self.assert_title('変更する 本 を選択')
        rows = self.get_result_list_rows()
        self.assertEqual(rows, None)
        # スクリーンショット（4枚目）を撮る
        self.save_screenshot()

        # 5) Bookモデル一覧画面で「本 を追加」リンクを押下
        self.selenium.find_element_by_link_text('本 を追加').click()
        self.wait_page_loaded()
        # Bookモデル追加画面が表示されていることを確認
        self.assert_title('本 を追加')
        # スクリーンショット（5枚目）を撮る
        self.save_screenshot()

        # 6) Bookモデル追加画面で項目を入力して「保存」ボタンを押下
        self.selenium.find_element_by_name('title').send_keys('Book 1')
        self.selenium.find_element_by_name('price').send_keys('1000')
        self.selenium.find_element_by_xpath(
            '//select[@name="size"]/option[text()="%s"]' % 'A4 - 210 x 297 mm'
        ).click()
        self.selenium.find_element_by_name('publish_date').send_keys('2020-09-01')
        self.selenium.find_element_by_xpath(
            '//input[@value="%s"]' % '保存').click()
        self.wait_page_loaded()
        # Bookモデル一覧画面が表示されていることを確認
        self.assert_title('変更する 本 を選択')
        rows = self.get_result_list_rows()
        self.assertEqual(len(rows), 1)
        # レコードが追加されていることを確認
        self.assertTrue(Book.objects.filter(title='Book 1').exists())
        # スクリーンショット（6枚目）を撮る
        self.save_screenshot()

        # 7) Bookモデル一覧画面で追加した本のリンクを押下
        rows = self.get_result_list_rows()
        rows[0].find_element_by_tag_name('a').click()
        self.wait_page_loaded()
        # Bookモデル変更画面が表示されていることを確認
        self.assert_title('本 を変更')
        # スクリーンショット（7枚目）を撮る
        self.save_screenshot()

        # 8) Bookモデル変更画面で項目を変更して「保存」ボタンを押下
        self.selenium.find_element_by_name('price').clear()
        self.selenium.find_element_by_name('price').send_keys('2000')
        self.selenium.find_element_by_xpath(
            '//input[@value="%s"]' % '保存').click()
        self.wait_page_loaded()
        # Bookモデル一覧画面が表示されていることを確認
        self.assert_title('変更する 本 を選択')
        rows = self.get_result_list_rows()
        self.assertEqual(len(rows), 1)
        # レコードが更新されていることを確認
        book = Book.objects.get(title='Book 1')
        self.assertEqual(book.price, 2000)
        # スクリーンショット（8枚目）を撮る
        self.save_screenshot()

        # 9) Bookモデル一覧画面で追加した本のチェックボックスを選択し、
        #    アクション一覧から「選択された 本 の削除」を選択して「実行」ボタンを押下
        rows = self.get_result_list_rows()
        rows[0].find_element_by_xpath('//input[@type="checkbox"]').click()
        self.selenium.find_element_by_xpath(
            '//select[@name="action"]//option[text()="%s"]' % '選択された 本 の削除'
        ).click()
        self.selenium.find_element_by_xpath(
            '//form[@id="changelist-form"]//button[@type="submit"]').click()
        # Bookモデル削除確認画面が表示されていることを確認
        self.assert_title('よろしいですか？')
        # スクリーンショット（9枚目）を撮る
        self.save_screenshot()

        # 10) Bookモデル削除確認画面で「はい」ボタンを押下
        self.selenium.find_element_by_xpath(
            '//input[@value="%s"]' % 'はい').click()
        self.wait_page_loaded()
        # Bookモデル一覧画面が表示されていることを確認
        self.assert_title('変更する 本 を選択')
        rows = self.get_result_list_rows()
        self.assertEqual(rows, None)
        # レコードが削除されていることを確認
        self.assertFalse(Book.objects.filter(title='Book 1').exists())
        # スクリーンショット（10枚目）を撮る
        self.save_screenshot()


class TestAdminSenarioByViewStaff(CustomAdminSeleniumTestCase):
    """管理サイトのシナリオテスト（閲覧専用スタッフの場合）"""

    PASSWORD = 'pass12345'

    def setUp(self):
        super().setUp()
        # テストユーザー（閲覧用スタッフ）を作成
        self.user = User.objects.create_user(
            'staff', 'staff@example.com', self.PASSWORD, is_staff=True)
        self.user.user_permissions.set(
            Permission.objects.filter(codename='view_book'))

    def test_book_crud_by_view_only_staff(self):
        """BookモデルのCRUD検証"""

        # 1) ログイン画面に遷移
        self.selenium.get(self.live_server_url + '/admin/')
        self.wait_page_loaded()
        self.assert_title('ログイン')
        # スクリーンショットを撮る
        self.save_screenshot()

        # 2) 閲覧用スタッフでログイン
        #    -> ホーム画面に遷移
        self.admin_login(self.user.username, self.PASSWORD)
        self.assert_title('ホーム')
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
