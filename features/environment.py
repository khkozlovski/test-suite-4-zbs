"""Behave environment hooks: WebDriver lifecycle management.

Run with a visible browser:      HEADLESS=false behave
Run headless (default, CI-safe): behave
"""
import os
import sys

# Make sure the project root (parent of "features/") is importable, so
# "from config import ..." and "from pages....import ..." work no matter
# how/where the `behave` command is invoked from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def before_all(context):
    context.headless = os.environ.get("HEADLESS", "true").lower() != "false"
    context.driver = _create_driver(context.headless)
    context.driver.implicitly_wait(0)  # we use explicit waits everywhere instead
    context.driver.maximize_window()


def _create_driver(headless):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1600,1200")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)


def before_scenario(context, scenario):
    # Every scenario starts from a clean slate (no leftover cookies).
    if context.driver.window_handles:
        context.driver.delete_all_cookies()


def after_scenario(context, scenario):
    # Close any extra tabs opened during the scenario (e.g. a PDF that
    # opened in a new tab) so the next scenario starts with a single tab.
    handles = context.driver.window_handles
    if len(handles) > 1:
        for handle in handles[1:]:
            context.driver.switch_to.window(handle)
            context.driver.close()
        context.driver.switch_to.window(handles[0])


def after_all(context):
    context.driver.quit()
