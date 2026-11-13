import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://127.0.0.1:5000"

def test_admin_flow_and_theme_toggle():
    """
    T6: Playwright E2E test exercising:
    - Admin login
    - Dashboard KPIs and Audit Trail
    - Theme toggle (light -> dark -> persistence upon reload -> light)
    - User list, search, clear search
    - User CRUD (add with role selection -> verify in list -> delete modal confirmation)
    - Zero console errors and zero 4xx/5xx network errors
    """
    console_errors = []
    failed_requests = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("response", lambda resp: failed_requests.append(f"{resp.status} {resp.url}") if resp.status >= 400 else None)

        # 1. Login
        page.goto(f"{BASE_URL}/auth/login")
        expect(page).to_have_title("Sign In - University Management System")
        page.fill("input[name='email']", "admin@ums.edu")
        page.fill("input[name='password']", "Admin@123")
        page.click("button[type='submit']")

        # 2. Admin Dashboard
        page.wait_for_url(f"{BASE_URL}/dashboard")
        expect(page.locator("main").get_by_text("Administrative Overview")).to_be_visible()
        expect(page.locator("main").get_by_text("Audit Trail")).to_be_visible()

        # 3. Theme Toggle & Persistence
        html = page.locator("html")
        initial_theme = html.get_attribute("data-bs-theme")
        page.click("#themeToggleBtn")
        page.wait_for_timeout(300)
        toggled_theme = html.get_attribute("data-bs-theme")
        assert toggled_theme != initial_theme, f"Theme should toggle, remained {initial_theme}"

        # Reload to verify persistence in localStorage
        page.reload()
        reloaded_theme = html.get_attribute("data-bs-theme")
        assert reloaded_theme == toggled_theme, f"Theme should persist upon reload, got {reloaded_theme}"

        # Restore light theme
        if reloaded_theme == "dark":
            page.click("#themeToggleBtn")
            page.wait_for_timeout(300)

        # 4. Users List & Search
        page.goto(f"{BASE_URL}/admin/users")
        expect(page.locator("main").get_by_text("User Accounts")).to_be_visible()

        # Search for 'tariq'
        page.fill("input[name='search']", "tariq")
        page.press("input[name='search']", "Enter")
        expect(page.locator("main").get_by_text("Tariq Mahmood")).to_be_visible()

        # Clear search
        clear_btn = page.locator(".search-clear-btn")
        if clear_btn.is_visible():
            clear_btn.click()
            page.wait_for_load_state("networkidle")

        # 5. Add User
        import time
        test_email = f"e2e.tester.{int(time.time())}@ums.edu"
        page.goto(f"{BASE_URL}/admin/users/add")
        expect(page.locator("main").get_by_text("Create User")).to_be_visible()
        page.fill("input[name='first_name']", "E2E")
        page.fill("input[name='last_name']", "Tester")
        page.fill("input[name='email']", test_email)
        page.fill("input[name='phone']", "03009998877")
        page.fill("input[name='password']", "TestPass@123")
        # Select first role option
        page.select_option("select[name='role_id']", index=1)
        page.click("button[type='submit']")

        # Redirect back to list
        page.wait_for_url(f"{BASE_URL}/admin/users*")

        # Verify created user is listed
        page.goto(f"{BASE_URL}/admin/users?search={test_email}")
        expect(page.locator("main").get_by_text(test_email)).to_be_visible()

        # Delete user via Delete Modal confirmation
        delete_btn = page.locator("button[data-bs-target^='#deleteModal']").first
        delete_btn.click()
        page.wait_for_timeout(500)
        confirm_btn = page.locator(".modal.show button[type='submit']").first
        confirm_btn.click()
        page.wait_for_load_state("networkidle")

        # Verify deleted
        page.goto(f"{BASE_URL}/admin/users?search={test_email}")
        expect(page.locator("main").get_by_text("No User Accounts Found")).to_be_visible()

        # Logout
        page.goto(f"{BASE_URL}/auth/logout")
        browser.close()

    # Filter out favicon or known harmless 404s
    critical_network_errors = [err for err in failed_requests if "favicon" not in err]
    assert len(console_errors) == 0, f"Encountered JS console errors: {console_errors}"
    assert len(critical_network_errors) == 0, f"Encountered failed HTTP requests: {critical_network_errors}"

def test_teacher_flow():
    """Verify teacher dashboard, sections, and timetable display."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        page.goto(f"{BASE_URL}/auth/login")
        page.fill("input[name='email']", "dr.tariq@ums.edu")
        page.fill("input[name='password']", "Teacher@123")
        page.click("button[type='submit']")

        page.wait_for_url(f"{BASE_URL}/dashboard")
        expect(page.locator("main h3:has-text('Assigned Course Sections')")).to_be_visible()
        expect(page.locator("main h3:has-text('Weekly Schedule')")).to_be_visible()

        page.goto(f"{BASE_URL}/auth/logout")
        browser.close()

def test_student_flow():
    """Verify student dashboard, dynamic rings, schedule, and fees in PKR."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        page.goto(f"{BASE_URL}/auth/login")
        page.fill("input[name='email']", "ali.raza@ums.edu")
        page.fill("input[name='password']", "Student@123")
        page.click("button[type='submit']")

        page.wait_for_url(f"{BASE_URL}/dashboard")
        expect(page.locator("main h2:has-text('Course Attendance')")).to_be_visible()
        expect(page.locator("main h3:has-text('Weekly Timetable')")).to_be_visible()
        expect(page.locator("main").get_by_text("PKR 0.00")).to_be_visible()

        # Check action buttons on list page are hidden for student (Issue #4)
        page.goto(f"{BASE_URL}/finance/invoices")
        expect(page.locator("main a.btn:has-text('Add')")).to_have_count(0)
        expect(page.locator("main button:has-text('Delete')")).to_have_count(0)

        page.goto(f"{BASE_URL}/auth/logout")
        browser.close()

def test_staff_flow():
    """Verify staff dashboard and services portal."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        page.goto(f"{BASE_URL}/auth/login")
        page.fill("input[name='email']", "staff.kamran@ums.edu")
        page.fill("input[name='password']", "Staff@123")
        page.click("button[type='submit']")

        page.wait_for_url(f"{BASE_URL}/dashboard")
        expect(page.locator("main h2:has-text('Campus Services & Operations')")).to_be_visible()
        expect(page.locator("main h3:has-text('Service Operations Modules')")).to_be_visible()

        page.goto(f"{BASE_URL}/auth/logout")
        browser.close()
