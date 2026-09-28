"""Step definitions for features/website.feature.

Note on Given vs. Then with identical wording: Behave keeps a separate
registry per keyword type (given/when/then), so the same sentence can be
implemented twice - once to *assert* a state (Then) and once to *arrange*
it from scratch (Given) - without any ambiguity error. Each Given step
below is therefore self-contained: it performs whatever navigation is
needed to reach that state, since Behave does not carry state between
scenarios.
"""
import time

import requests
from behave import given, when, then
from selenium.webdriver.support.ui import WebDriverWait

from config import BASE_URL
from pages.contact_page import ContactPage
from pages.main_page import MainPage

PDF_OPEN_TIMEOUT = 15


# ----------------------------------------------------------------------
# Page Object accessors (lazily attached to the scenario context)
# ----------------------------------------------------------------------
def _main_page(context):
    if not hasattr(context, "main_page"):
        context.main_page = MainPage(context.driver)
    return context.main_page


def _contact_page(context):
    if not hasattr(context, "contact_page"):
        context.contact_page = ContactPage(context.driver)
    return context.contact_page


# ----------------------------------------------------------------------
# PDF-opening helpers (a PDF may open in the same tab or a new one)
# ----------------------------------------------------------------------
def _remember_window(context):
    context.main_window = context.driver.current_window_handle
    context.handles_before = context.driver.window_handles


def _wait_and_switch_to_pdf(context, timeout=PDF_OPEN_TIMEOUT):
    driver = context.driver
    deadline = time.time() + timeout

    while time.time() < deadline:
        handles = driver.window_handles
        new_handles = [h for h in handles if h not in context.handles_before]
        if new_handles:
            driver.switch_to.window(new_handles[0])
            break
        if driver.current_url.lower().endswith(".pdf"):
            break
        time.sleep(0.2)

    WebDriverWait(driver, timeout).until(
        lambda d: d.current_url.lower().endswith(".pdf")
    )


def _assert_pdf_opened(context):
    driver = context.driver
    WebDriverWait(driver, PDF_OPEN_TIMEOUT).until(
        lambda d: d.current_url.lower().endswith(".pdf")
    )
    assert driver.current_url.lower().endswith(".pdf"), (
        f"Expected a PDF to be open, current url is {driver.current_url}"
    )


# ----------------------------------------------------------------------
# Given: Website is online
# ----------------------------------------------------------------------
@given("Website is online")
def step_given_website_online(context):
    response = requests.get(BASE_URL, timeout=10)
    assert response.status_code == 200, (
        f"Expected {BASE_URL} to be online, got status {response.status_code}"
    )


# ----------------------------------------------------------------------
# When: User visits the Website
# ----------------------------------------------------------------------
@when("User visits the Website")
def step_when_visit_website(context):
    _main_page(context).load()


# ----------------------------------------------------------------------
# The Main page is loaded correctly
# ----------------------------------------------------------------------
@then("The Main page is loaded correctly")
def step_then_main_page_loaded(context):
    assert _main_page(context).is_loaded(), "Main page did not load correctly"


@given("The Main page is loaded correctly")
def step_given_main_page_loaded(context):
    main_page = _main_page(context)
    main_page.load()
    assert main_page.is_loaded(), "Main page did not load correctly"


# ----------------------------------------------------------------------
# User clicks/taps the "Kontakt" banner
# ----------------------------------------------------------------------
@when('User clicks/taps the "Kontakt" banner')
def step_when_click_kontakt(context):
    _main_page(context).click_kontakt()


# ----------------------------------------------------------------------
# The User is navigated to the Contact page
# ----------------------------------------------------------------------
@then("The User is navigated to the Contact page")
def step_then_contact_page_loaded(context):
    assert _contact_page(context).is_loaded(), "Contact page did not load correctly"


@given("The User is navigated to the Contact page")
def step_given_contact_page_loaded(context):
    main_page = _main_page(context)
    main_page.load()
    main_page.click_kontakt()
    assert _contact_page(context).is_loaded(), "Contact page did not load correctly"


# ----------------------------------------------------------------------
# User clicks/taps the "Archiwum" banner
# ----------------------------------------------------------------------
@when('User clicks/taps the "Archiwum" banner')
def step_when_click_archiwum(context):
    _contact_page(context).click_archiwum()


# ----------------------------------------------------------------------
# User clicks/taps on an issue cover / summary / number
# ----------------------------------------------------------------------
@when("User clicks/taps on an issue cover")
def step_when_click_issue_cover(context):
    main_page = _main_page(context)
    _remember_window(context)
    if main_page.is_cover_only_section_visible():
        main_page.click_first_cover_only_issue()
    else:
        main_page.click_first_issue_cover()
    _wait_and_switch_to_pdf(context)


@when("User clicks/taps on an issue summary")
def step_when_click_issue_summary(context):
    main_page = _main_page(context)
    _remember_window(context)
    main_page.click_first_issue_summary()
    _wait_and_switch_to_pdf(context)


@when("User clicks/taps on an issue number")
def step_when_click_issue_number(context):
    main_page = _main_page(context)
    _remember_window(context)
    main_page.click_first_number_only_issue()
    _wait_and_switch_to_pdf(context)


# ----------------------------------------------------------------------
# User scrolls down
# ----------------------------------------------------------------------
@when("User scrolls down")
def step_when_scroll_down(context):
    _main_page(context).scroll_down_to_next_section()


# ----------------------------------------------------------------------
# User encounters issues displayed without a summary
# ----------------------------------------------------------------------
@then("User encounters issues displayed without a summary")
def step_then_no_summary_issues(context):
    main_page = _main_page(context)
    assert main_page.groups_cover_only(), "No cover-only issues found on the page"
    assert main_page.is_cover_only_section_visible(), (
        "Issues without a summary are not visible in the viewport"
    )


@given("User encounters issues displayed without a summary")
def step_given_no_summary_issues(context):
    main_page = _main_page(context)
    main_page.load()
    main_page.scroll_to_first_cover_only_issue()
    assert main_page.is_cover_only_section_visible(), (
        "Issues without a summary are not visible in the viewport"
    )


# ----------------------------------------------------------------------
# User encounters issues displayed without a cover
# ----------------------------------------------------------------------
@then("User encounters issues displayed without a cover")
def step_then_no_cover_issues(context):
    main_page = _main_page(context)
    assert main_page.groups_number_only(), "No cover-less issues found on the page"
    assert main_page.is_number_only_section_visible(), (
        "Issues without a cover are not visible in the viewport"
    )


@given("User encounters issues displayed without a cover")
def step_given_no_cover_issues(context):
    main_page = _main_page(context)
    main_page.load()
    main_page.scroll_to_first_number_only_issue()
    assert main_page.is_number_only_section_visible(), (
        "Issues without a cover are not visible in the viewport"
    )


# ----------------------------------------------------------------------
# The pdf containing the issue is opened
# ----------------------------------------------------------------------
@then("The pdf containing the issue is opened")
def step_then_pdf_opened(context):
    _assert_pdf_opened(context)


@given("The pdf containing the issue is opened")
def step_given_pdf_opened(context):
    main_page = _main_page(context)
    main_page.load()
    _remember_window(context)
    main_page.click_first_issue_cover()
    _wait_and_switch_to_pdf(context)
    _assert_pdf_opened(context)


# ----------------------------------------------------------------------
# User uses browser navigation to go back
# ----------------------------------------------------------------------
@when("User uses browser navigation to go back")
def step_when_browser_back(context):
    driver = context.driver
    if (
        len(driver.window_handles) > 1
        and driver.current_window_handle != context.main_window
    ):
        # The PDF opened in a new tab: close it and return to the main tab.
        driver.close()
        driver.switch_to.window(context.main_window)
    else:
        driver.back()
