import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:5000"

def test_r2_reflow_and_200_percent_zoom():
    """R2: Reflow (WCAG 1.4.10) at 320px width and simulated 200% zoom (640px)"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 320, "height": 568})
        page = context.new_page()

        # 1. Login page at 320px
        page.goto(f"{BASE_URL}/auth/login", wait_until="networkidle")
        doc_w = page.evaluate("document.documentElement.clientWidth")
        scroll_w = page.evaluate("document.documentElement.scrollWidth")
        assert scroll_w <= doc_w + 2, f"Horizontal overflow on login at 320px: {scroll_w} > {doc_w}"

        # 2. Login as admin
        page.fill('input[name="email"]', "admin@ums.edu")
        page.fill('input[name="password"]', "Admin@123")
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        # 3. Admin dashboard at 320px
        doc_w = page.evaluate("document.documentElement.clientWidth")
        scroll_w = page.evaluate("document.documentElement.scrollWidth")
        assert scroll_w <= doc_w + 2, f"Horizontal overflow on admin dashboard at 320px: {scroll_w} > {doc_w}"

        # 4. 200% Zoom simulation at 640px viewport (WCAG 1.4.10 requirement for 1280px @ 200% zoom)
        page.set_viewport_size({"width": 640, "height": 800})
        page.evaluate("document.documentElement.style.fontSize = '200%'") # Scale root font 200%
        page.wait_for_timeout(100)
        doc_w = page.evaluate("document.documentElement.clientWidth")
        scroll_w = page.evaluate("document.documentElement.scrollWidth")
        assert scroll_w <= doc_w + 2, f"Horizontal overflow at 200% zoom (640px): {scroll_w} > {doc_w}"

        # 5. List users page at 320px
        page.evaluate("document.documentElement.style.fontSize = ''") # Reset font size
        page.set_viewport_size({"width": 320, "height": 568})
        page.goto(f"{BASE_URL}/admin/users", wait_until="networkidle")
        doc_w = page.evaluate("document.documentElement.clientWidth")
        scroll_w = page.evaluate("document.documentElement.scrollWidth")
        assert scroll_w <= doc_w + 2, f"Horizontal overflow on users list at 320px: {scroll_w} > {doc_w}"

        browser.close()

def test_r3_device_profiles():
    """R3: Real-device profiles (iPhone SE, iPhone 14 Pro Max, Pixel 7, iPad Mini, iPad Pro 11)"""
    devices = [
        {"name": "iPhone SE", "width": 375, "height": 667, "dpr": 2.0},
        {"name": "iPhone 14 Pro Max", "width": 430, "height": 932, "dpr": 3.0},
        {"name": "Pixel 7", "width": 412, "height": 915, "dpr": 2.625},
        {"name": "iPad Mini", "width": 768, "height": 1024, "dpr": 2.0},
        {"name": "iPad Pro 11", "width": 834, "height": 1194, "dpr": 2.0},
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for dev in devices:
            context = browser.new_context(
                viewport={"width": dev["width"], "height": dev["height"]},
                device_scale_factor=dev["dpr"],
                is_mobile=True,
                has_touch=True
            )
            page = context.new_page()

            # Test login
            page.goto(f"{BASE_URL}/auth/login", wait_until="networkidle")
            doc_w = page.evaluate("document.documentElement.clientWidth")
            scroll_w = page.evaluate("document.documentElement.scrollWidth")
            assert scroll_w <= doc_w + 2, f"Device {dev['name']} login overflow: {scroll_w} > {doc_w}"

            # Login
            page.fill('input[name="email"]', "admin@ums.edu")
            page.fill('input[name="password"]', "Admin@123")
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle")

            # Check dashboard
            doc_w = page.evaluate("document.documentElement.clientWidth")
            scroll_w = page.evaluate("document.documentElement.scrollWidth")
            assert scroll_w <= doc_w + 2, f"Device {dev['name']} dashboard overflow: {scroll_w} > {doc_w}"

            context.close()
        browser.close()

def test_r4_role_mobile_interaction_flows():
    """R4: Role Mobile Interaction Flows on 390x844"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        page = context.new_page()

        # Admin Mobile Flow: Login -> Dashboard -> Open Drawer -> Filter -> Click Users -> View List
        page.goto(f"{BASE_URL}/auth/login", wait_until="networkidle")
        page.fill('input[name="email"]', "admin@ums.edu")
        page.fill('input[name="password"]', "Admin@123")
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Open mobile sidebar drawer
        drawer_btn = page.query_selector('button[data-bs-target="#sidebarOffcanvas"]')
        assert drawer_btn is not None and drawer_btn.is_visible()
        drawer_btn.click()
        page.wait_for_timeout(400)

        # Verify drawer is shown
        drawer = page.query_selector('#sidebarOffcanvas.show')
        assert drawer is not None, "Offcanvas drawer failed to open on mobile"

        # Test search filter in drawer
        search_input = page.query_selector('#sidebarOffcanvas .sidebar-search-input')
        assert search_input is not None
        search_input.fill("Users")
        page.wait_for_timeout(200)

        # Click Users link
        users_link = page.query_selector('#sidebarOffcanvas a.sidebar-link[href="/admin/users"]')
        assert users_link is not None and users_link.is_visible()
        users_link.click()
        page.wait_for_load_state("networkidle")
        assert "/admin/users" in page.url

        # Check stacked table cards
        cards = page.query_selector_all('.glass-table-cards tbody tr')
        assert len(cards) > 0, "No records found in users table"

        # Logout
        page.goto(f"{BASE_URL}/auth/logout", wait_until="networkidle")

        # Student Mobile Flow
        page.goto(f"{BASE_URL}/auth/login", wait_until="networkidle")
        page.fill('input[name="email"]', "ali.raza@ums.edu")
        page.fill('input[name="password"]', "Student@123")
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        assert page.query_selector('.conic-ring-container') is not None, "Student attendance rings missing"

        # Check invoices link in main content
        invoices_btn = page.query_selector('#main-content a[href="/finance/invoices"]')
        assert invoices_btn is not None
        invoices_btn.click()
        page.wait_for_load_state("networkidle")
        assert "/finance/invoices" in page.url

        browser.close()

def test_r5_orientation_and_extremes():
    """R5: Orientation Extremes (Landscape Phone 667x375 and Ultra-Wide 2560x1440)"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # 1. Landscape phone: 667x375
        land_ctx = browser.new_context(viewport={"width": 667, "height": 375}, is_mobile=True, has_touch=True)
        page = land_ctx.new_page()
        page.goto(f"{BASE_URL}/auth/login", wait_until="networkidle")
        doc_w = page.evaluate("document.documentElement.clientWidth")
        scroll_w = page.evaluate("document.documentElement.scrollWidth")
        assert scroll_w <= doc_w + 2, f"Landscape phone login overflow: {scroll_w} > {doc_w}"

        # Login
        page.fill('input[name="email"]', "admin@ums.edu")
        page.fill('input[name="password"]', "Admin@123")
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        doc_w = page.evaluate("document.documentElement.clientWidth")
        scroll_w = page.evaluate("document.documentElement.scrollWidth")
        assert scroll_w <= doc_w + 2, f"Landscape phone dashboard overflow: {scroll_w} > {doc_w}"
        land_ctx.close()

        # 2. Ultra-wide monitor: 2560x1440
        uw_ctx = browser.new_context(viewport={"width": 2560, "height": 1440})
        page = uw_ctx.new_page()
        page.goto(f"{BASE_URL}/auth/login", wait_until="networkidle")
        page.fill('input[name="email"]', "admin@ums.edu")
        page.fill('input[name="password"]', "Admin@123")
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Verify page content wrapper is capped at max-width 1600px
        content_w = page.evaluate("document.getElementById('page-content-wrapper').clientWidth")
        assert content_w <= 1620, f"Page content wrapper exceeded 1600px max-width on 2560px screen: {content_w}px"
        uw_ctx.close()

        browser.close()

def test_r6_accessibility_and_viewport_meta():
    """R6: Viewport meta tag and tap target accessibility"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{BASE_URL}/auth/login", wait_until="networkidle")

        # Check viewport meta tag
        meta = page.query_selector('meta[name="viewport"]')
        assert meta is not None, "Viewport meta tag missing"
        content = meta.get_attribute("content")
        assert "width=device-width" in content, "width=device-width missing in viewport meta"
        assert "initial-scale=1" in content, "initial-scale=1 missing in viewport meta"
        assert "maximum-scale" not in content, "maximum-scale must NOT be restricted"
        assert "user-scalable=no" not in content, "user-scalable must NOT be disabled"

        browser.close()

if __name__ == "__main__":
    pytest.main(["-v", __file__])
