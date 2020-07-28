import lxml.html
from django.test import TestCase


class ChangeListPage:
    """モデル一覧画面の画面項目検証用クラス"""

    def __init__(self, rendered_content):
        self.parsed_content = lxml.html.fromstring(rendered_content)

    @property
    def result_list(self):
        """検索結果表示テーブルの要素オブジェクト"""
        elements = self.parsed_content.xpath('//table[@id="result_list"]')
        return elements[0] if elements else None

    @property
    def result_list_head_texts(self):
        """検索結果表示テーブルのヘッダの表示内容"""
        if self.result_list is None:
            return None
        head = self.result_list.xpath('thead/tr')[0]
        return [
            e.text_content() for e in
            head.xpath('th[contains(@class, "column-")]/div[@class="text"]')
        ]

    @property
    def result_list_rows_texts(self):
        """検索結果表示テーブルの行ごとの表示内容"""
        if self.result_list is None:
            return None
        rows = self.result_list.xpath('tbody/tr')
        return [[
            e.text_content() for e in
            row.xpath('td[contains(@class, "field-")]')
        ] for row in rows]

    @property
    def result_count_text(self):
        """合計件数の表示内容"""
        elements = self.parsed_content.xpath(
            '//form[@id="changelist-form"]/p[@class="paginator"]')
        return elements[0].text.strip() if elements else None

    @property
    def action_list(self):
        """アクション一覧の要素オブジェクト"""
        elements = self.parsed_content.xpath(
            '//form[@id="changelist-form"]/div[@class="actions"]')
        return elements[0] if elements else None

    @property
    def action_list_texts(self):
        """アクション一覧の表示内容"""
        if self.action_list is None:
            return None
        elements = self.action_list.xpath('//select/option')
        return [e.text for e in elements]

    @property
    def add_button(self):
        """追加ボタンの要素オブジェクト"""
        elements = self.parsed_content.xpath('//a[@class="addlink"]')
        return elements[0] if elements else None

    @property
    def search_form(self):
        """簡易検索フォームの要素オブジェクト"""
        elements = self.parsed_content.xpath('//form[@id="changelist-search"]')
        return elements[0] if elements else None

    @property
    def filter(self):
        """絞り込み（フィルタ）の要素オブジェクト"""
        elements = self.parsed_content.xpath('//div[@id="changelist-filter"]')
        return elements[0] if elements else None

    @property
    def filter_headers(self):
        """絞り込み（フィルタ）の h3タイトルの表示内容"""
        if self.filter is None:
            return None
        filter_headers = self.filter.xpath('/h3')
        return [e.text for e in filter_headers]

    @property
    def filter_choices_texts(self):
        """絞り込み（フィルタ）の選択肢の表示内容"""
        if self.filter is None:
            return None
        filter_rows = self.filter.xpath('/ul')
        return [[
            e.text_content().strip() for e in filter_row
        ] for filter_row in filter_rows]

    @property
    def success_message(self):
        """成功メッセージ"""
        elements = self.parsed_content.xpath(
            '//ul[@class="messagelist"]/li[@class="success"]')
        return elements[0].text_content() if elements else None


class LxmlTestMixin(TestCase):
    """
    """

    def assert_on_display(self, element):
        self.assertIsNotNone(element)
        # if isinstance(element, list):
        #     self.assertTrue(len(element) > 0)
        # else:
        #     self.assertIsNotNone(element)

    def assert_not_on_display(self, element):
        self.assertIsNone(element)
        # if isinstance(element, list):
        #     self.assertTrue(len(element) == 0)
        # else:
        #     self.assertIsNone(element)

    def assert_success_message(self, html, message):
        """成功メッセージを検証する"""
        # TODO
        self.assertEqual(
            html.xpath('//ul[@class="messagelist"]/li[@class="success"]'),
            [message]
        )

    def is_link_on_display(self, html, css_class):
        """リンクが表示されているかどうかを返す"""
        return len(html.xpath('//a[@class="%s"]' % css_class)) == 1

    # TODO
    def add_button_on_change_list_page(self, html, css_class):
        pass


class LxmlTestMixinForChangeList(LxmlTestMixin, TestCase):
    """管理サイトのモデル一覧画面のテスト用のMixin"""

    def get_result_list(self, html):
        """検索結果表示テーブルの要素を取得する"""
        if not html.xpath('//table[@id="result_list"]'):
            return None, []
        table = html.xpath('//table[@id="result_list"]')[0]
        head = table.xpath('thead/tr')[0]
        rows = table.xpath('tbody/tr')
        return head, rows

    def assert_thead(self, head, expected_texts):
        """検索結果表示テーブルのヘッダを検証する"""
        head_texts = [
            e.text_content() for e in
            head.xpath('th[contains(@class, "column-")]/div[@class="text"]')
        ]
        self.assertListEqual(head_texts, expected_texts)

    def assert_tbody_row(self, row, expected_texts):
        """検索結果表示テーブルのレコード行を検証する"""
        row_texts = [
            e.text_content() for e in
            row.xpath('td[contains(@class, "field-")]')
        ]
        self.assertListEqual(row_texts, expected_texts)

    def assert_result_count_message(self, html, message):
        """合計件数のメッセージを検証する"""
        self.assertIn(message, html.xpath(
            '//form[@id="changelist-form"]/p[@class="paginator"]')[0].text)

    def assert_actions(self, html, actions):
        """アクション一覧のラベルを検証する"""
        options = html.xpath(
            '//form[@id="changelist-form"]/div[@class="actions"]//select/option')
        self.assertEqual([e.text for e in options], actions)

    # def is_addlink_on_display(self, html):
    #     return self.is_link_on_display(html, 'addlink')

    def assert_addlink_is_on_display(self, html):
        """追加ボタンが表示されていることを検証する"""
        self.assertTrue(self.is_link_on_display(html, 'addlink'))

    def assert_addlink_is_not_on_display(self, html):
        """追加ボタンが表示されていないことを検証する"""
        self.assertFalse(self.is_link_on_display(html, 'addlink'))
