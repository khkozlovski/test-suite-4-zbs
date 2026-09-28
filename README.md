# zbs-website-tests

Behave (BDD) test suite for **https://zbs.net.pl**, written in Python using
the Page Object pattern.

## Project structure

```
zbs-website-tests/
├── config.py                     # BASE_URL, timeouts
├── requirements.txt
├── behave.ini                    # behave runner config
├── pages/                        # Page Objects
│   ├── base_page.py
│   ├── main_page.py
│   └── contact_page.py
└── features/
    ├── website.feature           # Gherkin scenarios
    ├── environment.py            # Before/after hooks (WebDriver lifecycle)
    └── steps/
        └── website_steps.py      # Step definitions
```

## Requirements

- Python 3.9+
- Google Chrome installed
- (Selenium 4.6+ auto-downloads a matching chromedriver via Selenium
  Manager - no extra driver setup needed)

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the tests

```bash
behave
```

By default the browser runs **headless**. To watch it run visibly:

```bash
# macOS/Linux
HEADLESS=false behave

# Windows (PowerShell)
$env:HEADLESS="false"; behave
```

Run a single scenario or feature:

```bash
behave features/website.feature
behave features/website.feature -n "User opens the Contact page"
```

## Opening the project in PyCharm

1. `File > Open...` and select the `zbs-website-tests` folder.
2. PyCharm will detect it as a plain Python project. Create the
   interpreter: `File > Settings > Project: zbs-website-tests >
   Python Interpreter > Add Interpreter > Add Local Interpreter`, choose
   **Virtualenv Environment > New**, and let PyCharm create `venv` in the
   project root (or point it at the `venv` you already created above).
3. Install dependencies: open the `requirements.txt` file, PyCharm will
   prompt "Install requirements" - accept, or run
   `pip install -r requirements.txt` in the PyCharm terminal.
4. Install the **Cucumber+** (Gherkin) plugin if you want `.feature` file
   syntax highlighting and the ability to click the green "run" arrow
   next to a scenario: `Settings > Plugins > Marketplace > search
   "Cucumber"`.
5. Mark the project root as a **Sources Root** if PyCharm doesn't resolve
   `from pages.main_page import MainPage` / `from config import
   BASE_URL` automatically: right-click the `zbs-website-tests` folder in
   the Project pane > `Mark Directory as > Sources Root`.
6. Run via the terminal (`behave`) or create a PyCharm Run Configuration:
   `Run > Edit Configurations > + > Behave` (if the plugin adds it) or a
   plain `Python` configuration that runs the `behave` module:
   - Module name: `behave`
   - Working directory: project root

## Pushing to GitHub

From the project root:

```bash
git init
git add .
git commit -m "Initial commit: Behave test suite for zbs.net.pl"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

Or directly from PyCharm: `VCS > Create Git Repository...`, stage/commit
the files (`Commit` tool window), then `Git > Push...` after adding a
GitHub remote (`Git > Manage Remotes... > Add`), or use `VCS > Share
Project on GitHub` if you're signed into a GitHub account in PyCharm.

## Design notes

- **Page Objects** (`pages/`) contain all Selenium locators and
  interactions. `BasePage` holds shared helpers (explicit waits, click,
  scrolling, viewport checks); `MainPage` and `ContactPage` extend it.
- **Environment hooks** (`features/environment.py`) create a single
  Chrome WebDriver session for the whole test run, clear cookies before
  each scenario, and close any stray tabs (e.g. an opened PDF) after
  each scenario.
- The archive page lists every issue as `<a href="...pdf">` links. Some
  issues have a cover image **and** summary/title text links, some have
  **only** a cover image, and the oldest ones have **only** a plain
  "Numer N" text link. `MainPage._issue_groups()` groups the links by
  the PDF they point to and classifies each group, so the step
  definitions can work with "the newest issue", "an issue without a
  summary" and "an issue without a cover" without hard-coding issue
  numbers - this keeps the suite working as new issues are published.
- Because `Given` steps re-use the exact wording of a previous
  scenario's `Then` step (a common Gherkin readability convention),
  each `Given` step is implemented independently from its `Then`
  counterpart: it performs whatever navigation/scrolling is needed to
  reach that state from scratch, since Behave scenarios don't share
  state with each other.
- Opening a PDF is handled defensively: the site may open it in the
  same tab or a new one, so the steps detect whichever happens and
  "going back" either calls `driver.back()` or closes the extra tab,
  whichever applies.

## Notes / things worth double-checking against the live site

I built the selectors and page structure from the currently published
markup at zbs.net.pl (link text `Kontakt` / `Archiwum`, `<img
src=".../logo3.png">`, `<a href="....pdf">` cover/summary/number links).
If the site's markup changes, the locators in `pages/main_page.py` and
`pages/contact_page.py` are the only place you should need to update.
