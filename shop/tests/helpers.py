import os
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


class TestAdminChangeListMixin:
    """管理サイトのモデル一覧画面のテスト用のMixin"""

    def get_result_list(self, html):
        """検索結果テーブルの要素を取得する"""
        if not html.xpath('//table[@id="result_list"]'):
            return None, []
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

    def assert_success_messages(self, html, messages):
        """成功メッセージを検証する"""
        # TODO
        self.assertEqual(
            html.xpath('//ul[@class="messagelist"]/li[@class="success"]'),
            messages
        )

    def assert_actions(self, html, actions):
        """アクション一覧のラベルを検証する"""
        options = html.xpath(
            '//form[@id="changelist-form"]/div[@class="actions"]//select/option')
        self.assertEqual([e.text for e in options], actions)

    def assert_link_is_displayed(self, html, css_class):
        """リンクが表示されていることを検証する"""
        self.assertTrue(len(html.xpath('//a[@class="%s"]' % css_class)) == 1)

    def assert_link_is_not_displayed(self, html, css_class):
        """リンクが表示されていないことを検証する"""
        self.assertTrue(len(html.xpath('//a[@class="%s"]' % css_class)) == 0)


class TestAdminSenarioMixin:
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
