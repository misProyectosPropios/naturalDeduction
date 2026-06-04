from pathlib import Path
from playwright.sync_api import sync_playwright


def test_index_html_flow():
    root = Path(__file__).resolve().parent
    index_path = root / 'index.html'
    assert index_path.exists(), 'index.html must exist for the browser test'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(index_path.as_uri())

        # Add a context formula
        page.fill('#formulaInput', '"P"')
        page.click('#addBtn')
        assert 'P' in page.locator('#formulaList').inner_text()

        # Add a goal formula
        page.fill('#formulaInput', '"P" -> "P"')
        page.click('#setGoalBtn')
        view_text = page.locator('#viewArea pre').inner_text()
        assert 'Goal: (P → P)' in view_text or 'Goal: P → P' in view_text

        # Change goal by adding a new goal formula
        page.fill('#formulaInput', '"Q" -> "Q"')
        page.click('#setGoalBtn')
        view_text = page.locator('#viewArea pre').inner_text()
        assert 'Goal: (Q → Q)' in view_text or 'Goal: Q → Q' in view_text

        # Delete the existing context item
        remove_buttons = page.locator('#formulaList .remove')
        assert remove_buttons.count() == 1
        remove_buttons.first.click()
        assert 'No context formulas added yet.' in page.locator('#formulaList').inner_text()

        # Add a context and set a goal to prove
        page.fill('#formulaInput', '"P"')
        page.click('#addBtn')
        page.fill('#formulaInput', '"P" -> "P"')
        page.click('#setGoalBtn')

        # Apply implication introduction to prove the formula
        page.select_option('#stepSelect', value='0')
        page.select_option('#ruleSelect', value='IMPLICATION_INTRODUCTION')
        page.click('#applyRuleBtn')

        step_text = page.locator('#stepsList .step-item').inner_text()
        assert '→I' in step_text or '→ I' in step_text
        assert 'P' in step_text

        browser.close()
        print("Completed")

test_index_html_flow()