"""Page Object for the ZBS main (archive) page: https://zbs.net.pl

The archive page lists every issue of the magazine as a flat sequence of
<a href="...pdf"> links, in newest-to-oldest order. Depending on how old an
issue is, it is represented differently in the markup:

  * newest issues  -> a cover image AND several text links (title, date,
                       article names) all pointing at the same PDF
  * older issues    -> only a cover image pointing at the PDF (no summary
                       text links)
  * oldest issues   -> only a plain "Numer N" text link pointing at the PDF
                       (no cover image at all)

``_issue_groups`` walks the links in DOM order and groups them by the PDF
they point to, so the rest of the Page Object (and the step definitions)
can reason about "the newest issue", "an issue without a summary" and
"an issue without a cover" without hard-coding issue numbers.
"""
from selenium.webdriver.common.by import By

from config import BASE_URL
from pages.base_page import BasePage


class MainPage(BasePage):
    URL = BASE_URL
    PAGE_TITLE = "Z biegiem szyn"

    # The "Kontakt" banner may be plain text, an image, or an icon - so
    # instead of matching visible link text (fragile / doesn't work for
    # image-only links at all) we match on the link's destination first,
    # falling back to any text or image alt/title that mentions "kontakt".
    KONTAKT_LINK = (
        By.XPATH,
        "//a[contains(@href, 'kontakt') "
        "or contains(translate(normalize-space(.), "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'kontakt') "
        "or .//img[contains(translate(@alt, "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'kontakt') "
        "or contains(translate(@title, "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'kontakt')]]",
    )
    ISSUE_LINKS = (By.CSS_SELECTOR, "a[href$='.pdf']")

    # ------------------------------------------------------------------
    # Page-level actions
    # ------------------------------------------------------------------
    def load(self):
        self.open(self.URL)

    def is_loaded(self):
        return (
            self.current_url.rstrip("/").startswith(BASE_URL)
            and self.PAGE_TITLE in self.title
            and self.is_present(self.KONTAKT_LINK)
            and self.is_present(self.ISSUE_LINKS)
        )

    def click_kontakt(self):
        self.click(self.KONTAKT_LINK)

    # ------------------------------------------------------------------
    # Issue discovery / grouping
    # ------------------------------------------------------------------
    def _issue_groups(self):
        groups = []
        groups_by_href = {}

        for anchor in self.find_all(self.ISSUE_LINKS):
            href = anchor.get_attribute("href")
            has_image = len(anchor.find_elements(By.TAG_NAME, "img")) > 0
            text = anchor.text.strip()

            if href not in groups_by_href:
                group = {
                    "href": href,
                    "anchors": [],
                    "has_cover": False,
                    "has_text": False,
                }
                groups_by_href[href] = group
                groups.append(group)

            group = groups_by_href[href]
            group["anchors"].append(anchor)
            group["has_cover"] = group["has_cover"] or has_image
            group["has_text"] = group["has_text"] or bool(text)

        for group in groups:
            if group["has_cover"] and group["has_text"]:
                group["kind"] = "cover_and_summary"
            elif group["has_cover"]:
                group["kind"] = "cover_only"
            else:
                group["kind"] = "number_only"

        return groups

    def groups_with_summary(self):
        return [g for g in self._issue_groups() if g["kind"] == "cover_and_summary"]

    def groups_cover_only(self):
        return [g for g in self._issue_groups() if g["kind"] == "cover_only"]

    def groups_number_only(self):
        return [g for g in self._issue_groups() if g["kind"] == "number_only"]

    @staticmethod
    def _cover_anchor(group):
        for anchor in group["anchors"]:
            if anchor.find_elements(By.TAG_NAME, "img"):
                return anchor
        return group["anchors"][0]

    @staticmethod
    def _text_anchor(group):
        for anchor in group["anchors"]:
            if not anchor.find_elements(By.TAG_NAME, "img") and anchor.text.strip():
                return anchor
        return group["anchors"][0]

    # ------------------------------------------------------------------
    # Clicking issues
    # ------------------------------------------------------------------
    def click_first_issue_cover(self):
        """Click the cover image of the newest issue (has a summary)."""
        group = self.groups_with_summary()[0]
        self.click_element(self._cover_anchor(group))

    def click_first_issue_summary(self):
        """Click one of the newest issue's summary/title text links."""
        group = self.groups_with_summary()[0]
        self.click_element(self._text_anchor(group))

    def click_first_cover_only_issue(self):
        """Click the cover of the newest issue that has no summary text."""
        group = self.groups_cover_only()[0]
        self.click_element(self._cover_anchor(group))

    def click_first_number_only_issue(self):
        """Click the "Numer N" link of the newest issue that has no cover."""
        group = self.groups_number_only()[0]
        self.click_element(self._text_anchor(group))

    # ------------------------------------------------------------------
    # Scrolling helpers
    # ------------------------------------------------------------------
    def scroll_to_first_cover_only_issue(self):
        group = self.groups_cover_only()[0]
        self.scroll_into_view(self._cover_anchor(group))

    def scroll_to_first_number_only_issue(self):
        group = self.groups_number_only()[0]
        self.scroll_into_view(self._text_anchor(group))

    def is_cover_only_section_visible(self):
        group = self.groups_cover_only()[0]
        return self.is_in_viewport(self._cover_anchor(group))

    def is_number_only_section_visible(self):
        group = self.groups_number_only()[0]
        return self.is_in_viewport(self._text_anchor(group))

    def scroll_down_to_next_section(self):
        """Scroll towards the next not-yet-visible group of issues.

        First reveals the "cover only" issues, then the "number only"
        issues. Calling this repeatedly mimics a user scrolling down the
        page one section at a time.
        """
        if not self.is_cover_only_section_visible():
            self.scroll_to_first_cover_only_issue()
        elif not self.is_number_only_section_visible():
            self.scroll_to_first_number_only_issue()
        else:
            self.scroll_to_bottom()
