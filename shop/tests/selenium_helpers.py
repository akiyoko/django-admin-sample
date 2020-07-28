import os
from glob import glob

from selenium import webdriver

try:
    # importすることでChromeDriverのパスを通してくれる
    import chromedriver_binary
except ImportError:
    raise


class SeleniumTestMixin:
    """管理サイトのシナリオテスト用のMixin"""

    # スクリーンショットを保存するディレクトリ
    SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'screenshots')

    available_apps = None
    browser = 'chrome'

    def setUp(self):
        super().setUp()
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

        ファイル名は「<テストID>_(<連番>).png」
        例)
        - shop.tests.test_admin_senario.TestAdminSenario.test_book_crud.png
        - shop.tests.test_admin_senario.TestAdminSenario.test_book_crud_(1).png
        - shop.tests.test_admin_senario.TestAdminSenario.test_book_crud_(2).png
        """
        if not os.path.exists(self.SCREENSHOT_DIR):
            os.makedirs(self.SCREENSHOT_DIR, exist_ok=True)

        filename = '{}.png'.format(self.id())
        i = 0
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
