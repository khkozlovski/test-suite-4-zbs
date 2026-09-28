"""Common Selenium helper methods shared by every Page Object."""
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    TimeoutException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import DEFAULT_TIMEOUT


class BasePage:
    """Base class that all Page Objects inherit from."""

    def __init__(self, driver):
        self.driver = driver

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def open(self, url):
        self.driver.get(url)
        # Don't consider navigation "done" until the browser itself says
        # the document has finished loading (images/lazy content may
        # still be arriving after this, but the DOM/text is ready).
        self.wait().until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    # ------------------------------------------------------------------
    # Element lookup / waits
    # ------------------------------------------------------------------
    def wait(self, timeout=DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout)

    def find(self, locator, timeout=DEFAULT_TIMEOUT):
        return self.wait(timeout).until(EC.presence_of_element_located(locator))

    def find_all(self, locator, timeout=DEFAULT_TIMEOUT):
        return self.wait(timeout).until(EC.presence_of_all_elements_located(locator))

    def is_present(self, locator, timeout=DEFAULT_TIMEOUT):
        try:
            self.find(locator, timeout)
            return True
        except TimeoutException:
            return False

    def click(self, locator, timeout=DEFAULT_TIMEOUT):
        element = self.wait(timeout).until(EC.element_to_be_clickable(locator))
        self.click_element(element)
        return element

    def click_element(self, element):
        """Click a WebElement, falling back to a JS click.

        A plain Selenium click requires the element to have a non-zero
        rendered size (it fails with "element has zero size" on some
        lazy-loaded/off-screen elements even right after scrolling them
        into view). A JS click sidesteps that check entirely.
        """
        self.scroll_into_view(element)
        try:
            element.click()
        except (ElementNotInteractableException, ElementClickInterceptedException):
            self.driver.execute_script("arguments[0].click();", element)

    # ------------------------------------------------------------------
    # Scrolling
    # ------------------------------------------------------------------
    def scroll_into_view(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )

    def scroll_by(self, pixels):
        self.driver.execute_script(f"window.scrollBy(0, {pixels});")

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def is_in_viewport(self, element):
        return self.driver.execute_script(
            """
            const rect = arguments[0].getBoundingClientRect();
            const vw = window.innerWidth || document.documentElement.clientWidth;
            const vh = window.innerHeight || document.documentElement.clientHeight;
            return rect.top >= 0 && rect.left >= 0 && rect.bottom <= vh && rect.right <= vw;
            """,
            element,
        )

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------
    @property
    def current_url(self):
        return self.driver.current_url

    @property
    def title(self):
        return self.driver.title
