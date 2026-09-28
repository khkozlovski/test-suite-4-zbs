"""Page Object for the ZBS contact page: https://zbs.net.pl/kontakt.html"""
from selenium.webdriver.common.by import By

from config import BASE_URL, CONTACT_URL
from pages.base_page import BasePage


class ContactPage(BasePage):
    URL = CONTACT_URL

    # The "Archiwum" banner may be plain text or an image, so we match on
    # where the link points (the main page) first, then fall back to any
    # text or image alt/title that mentions "archiwum".
    _LOWER = (
        "translate({0}, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
    )
    _HOME_HREFS = (BASE_URL, f"{BASE_URL}/", f"{BASE_URL}/index.html")
    _HOME_CONDITIONS = " or ".join(f"@href='{h}'" for h in _HOME_HREFS)
    ARCHIWUM_LINK = (
        By.XPATH,
        f"//a[{_HOME_CONDITIONS} "
        "or contains(@href, 'index.html') "
        f"or contains({_LOWER.format('normalize-space(.)')}, 'archiwum') "
        f"or .//img[contains({_LOWER.format('@alt')}, 'archiwum') "
        f"or contains({_LOWER.format('@title')}, 'archiwum')]]",
    )

    def load(self):
        self.open(self.URL)

    def is_loaded(self):
        return (
            "kontakt" in self.current_url
            and self.is_present(self.ARCHIWUM_LINK)
        )

    def click_archiwum(self):
        self.click(self.ARCHIWUM_LINK)
