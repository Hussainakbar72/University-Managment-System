import os
import shutil
import sys
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:5000"
DOCS_DIR = os.path.abspath("docs/responsive/gate2")
BRAIN_DIR = os.path.abspath(r"C:\Users\HP\.gemini\antigravity\brain\a21b1625-059d-4ae6-9d62-0063dc5d0281\gate2_preview_images")

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

VIEWPORTS = [
    ("mobile_320", 320, 568),
    ("mobile_390", 390, 844),
    ("tablet_768", 768, 1024),
    ("tablet_1024", 1024, 768),
    ("desktop_1440", 1440, 900),
    ("desktop_1920", 1920, 1080),
]

THEMES = ["dark", "light"]

PAGES = [
    ("login", f"{BASE_URL}/auth/login", False),
    ("admin_dashboard", f"{BASE_URL}/dashboard/", True),
    ("list_users", f"{BASE_URL}/admin/users", True),
    ("form_add_user", f"{BASE_URL}/admin/users/add", True),
]

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        for vp_name, width, height in VIEWPORTS:
            print(f"=== Capturing Viewport: {vp_name} ({width}x{height}) ===")
            for theme in THEMES:
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    color_scheme="dark" if theme == "dark" else "light"
                )
                page = context.new_page()
                
                # First capture anonymous login
                login_url = f"{BASE_URL}/auth/login"
                page.goto(login_url, wait_until="networkidle")
                page.evaluate(f"document.documentElement.setAttribute('data-theme', '{theme}')")
                page.wait_for_timeout(200)
                
                filename = f"login_{vp_name}_{theme}.png"
                filepath = os.path.join(DOCS_DIR, filename)
                page.screenshot(path=filepath, full_page=True)
                shutil.copy2(filepath, os.path.join(BRAIN_DIR, filename))
                print(f"  Captured: {filename}")
                
                # Now login as ADMIN
                page.fill('input[name="email"]', "admin@ums.edu")
                page.fill('input[name="password"]', "Admin@123")
                page.click('button[type="submit"]')
                page.wait_for_load_state("networkidle")
                
                # Ensure theme persists
                page.evaluate(f"document.documentElement.setAttribute('data-theme', '{theme}')")
                
                # Dashboard
                dash_file = f"dashboard_{vp_name}_{theme}.png"
                dash_path = os.path.join(DOCS_DIR, dash_file)
                page.screenshot(path=dash_path, full_page=True)
                shutil.copy2(dash_path, os.path.join(BRAIN_DIR, dash_file))
                print(f"  Captured: {dash_file}")
                
                # If width < 1200, capture offcanvas drawer open
                if width < 1200:
                    drawer_btn = page.query_selector('button[data-bs-target="#mobileSidebar"]')
                    if drawer_btn and drawer_btn.is_visible():
                        drawer_btn.click()
                        page.wait_for_timeout(400) # wait for animation
                        drawer_file = f"sidebar_drawer_{vp_name}_{theme}.png"
                        drawer_path = os.path.join(DOCS_DIR, drawer_file)
                        page.screenshot(path=drawer_path)
                        shutil.copy2(drawer_path, os.path.join(BRAIN_DIR, drawer_file))
                        print(f"  Captured: {drawer_file}")
                        # Close drawer
                        close_btn = page.query_selector('#mobileSidebar .btn-close')
                        if close_btn and close_btn.is_visible():
                            close_btn.click()
                            page.wait_for_timeout(300)
                
                # Users list
                page.goto(f"{BASE_URL}/admin/users", wait_until="networkidle")
                page.evaluate(f"document.documentElement.setAttribute('data-theme', '{theme}')")
                list_file = f"list_users_{vp_name}_{theme}.png"
                list_path = os.path.join(DOCS_DIR, list_file)
                page.screenshot(path=list_path, full_page=True)
                shutil.copy2(list_path, os.path.join(BRAIN_DIR, list_file))
                print(f"  Captured: {list_file}")
                
                # Add user form
                page.goto(f"{BASE_URL}/admin/users/add", wait_until="networkidle")
                page.evaluate(f"document.documentElement.setAttribute('data-theme', '{theme}')")
                form_file = f"form_user_{vp_name}_{theme}.png"
                form_path = os.path.join(DOCS_DIR, form_file)
                page.screenshot(path=form_path, full_page=True)
                shutil.copy2(form_path, os.path.join(BRAIN_DIR, form_file))
                print(f"  Captured: {form_file}")
                
                context.close()
        
        browser.close()
    print("All Gate 2 preview screenshots successfully captured!")

if __name__ == "__main__":
    main()
