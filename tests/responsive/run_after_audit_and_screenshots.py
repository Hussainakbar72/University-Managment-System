import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import json
import time
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:5000"

AUDIT_VIEWPORTS = [
    {"name": "320x568_iphone_se", "width": 320, "height": 568},
    {"name": "390x844_iphone_13", "width": 390, "height": 844},
    {"name": "667x375_iphone_land", "width": 667, "height": 375},
    {"name": "768x1024_ipad_port", "width": 768, "height": 1024},
    {"name": "1024x768_ipad_land", "width": 1024, "height": 768},
    {"name": "1280x720_hd_laptop", "width": 1280, "height": 720},
    {"name": "1440x900_macbook", "width": 1440, "height": 900},
    {"name": "1920x1080_fhd_desk", "width": 1920, "height": 1080},
]

ALL_17_VIEWPORTS = [
    {"name": "320x568", "width": 320, "height": 568},
    {"name": "360x640", "width": 360, "height": 640},
    {"name": "390x844", "width": 390, "height": 844},
    {"name": "430x932", "width": 430, "height": 932},
    {"name": "667x375", "width": 667, "height": 375},
    {"name": "744x1133", "width": 744, "height": 1133},
    {"name": "768x1024", "width": 768, "height": 1024},
    {"name": "820x1180", "width": 820, "height": 1180},
    {"name": "1024x768", "width": 1024, "height": 768},
    {"name": "1024x1366", "width": 1024, "height": 1366},
    {"name": "1180x820", "width": 1180, "height": 820},
    {"name": "1280x720", "width": 1280, "height": 720},
    {"name": "1366x768", "width": 1366, "height": 768},
    {"name": "1440x900", "width": 1440, "height": 900},
    {"name": "1536x864", "width": 1536, "height": 864},
    {"name": "1920x1080", "width": 1920, "height": 1080},
    {"name": "2560x1440", "width": 2560, "height": 1440},
]

REPRESENTATIVE_FAMILIES = [
    {"family": "login", "role": "anonymous", "url": "/auth/login"},
    {"family": "admin_dashboard", "role": "admin", "url": "/dashboard"},
    {"family": "teacher_dashboard", "role": "teacher", "url": "/dashboard"},
    {"family": "student_dashboard", "role": "student", "url": "/dashboard"},
    {"family": "staff_dashboard", "role": "staff", "url": "/dashboard"},
    {"family": "crud_list_users", "role": "admin", "url": "/admin/users"},
    {"family": "crud_form_user_add", "role": "admin", "url": "/admin/users/add"},
    {"family": "auth_profile", "role": "admin", "url": "/auth/profile"},
    {"family": "report_students", "role": "admin", "url": "/reports/students"},
    {"family": "report_fees", "role": "admin", "url": "/reports/fees"},
    {"family": "error_403", "role": "teacher", "url": "/admin/users"},
    {"family": "error_404", "role": "anonymous", "url": "/nonexistent-page-404"},
]

AUDIT_JS = """
(() => {
    const docWidth = document.documentElement.clientWidth;
    const docScrollWidth = document.documentElement.scrollWidth;
    const bodyScrollWidth = document.body ? document.body.scrollWidth : 0;
    const hasHorizontalOverflow = (docScrollWidth > docWidth + 2) || (bodyScrollWidth > docWidth + 2);

    const overflowingElements = [];
    document.querySelectorAll('*').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.right > docWidth + 2 && rect.width > 0 && rect.height > 0) {
            const style = window.getComputedStyle(el);
            if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
                overflowingElements.push({
                    tag: el.tagName.toLowerCase(),
                    id: el.id,
                    className: el.className,
                    right: Math.round(rect.right),
                    docWidth: docWidth,
                    overflowPx: Math.round(rect.right - docWidth)
                });
            }
        }
    });

    const offscreenInteractive = [];
    document.querySelectorAll('button, a, input, select, textarea').forEach(el => {
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
            if (rect.left < -5 || rect.right > docWidth + 5) {
                offscreenInteractive.push({
                    tag: el.tagName.toLowerCase(),
                    text: (el.innerText || el.value || el.placeholder || '').trim().slice(0, 30),
                    left: Math.round(rect.left),
                    right: Math.round(rect.right)
                });
            }
        }
    });

    const clippedText = [];
    document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, label').forEach(el => {
        if (el.children.length === 0 && el.innerText.trim().length > 0) {
            const style = window.getComputedStyle(el);
            if (style.display !== 'none' && style.visibility !== 'hidden') {
                if (el.scrollWidth > el.clientWidth + 2 && style.overflow === 'hidden' && style.textOverflow !== 'ellipsis') {
                    clippedText.push({
                        tag: el.tagName.toLowerCase(),
                        text: el.innerText.trim().slice(0, 40),
                        scrollWidth: el.scrollWidth,
                        clientWidth: el.clientWidth
                    });
                }
            }
        }
    });

    const overlappingSiblings = [];
    const mainCards = Array.from(document.querySelectorAll('.glass-card, .btn, .topbar, .user-chip'));
    for (let i = 0; i < mainCards.length; i++) {
        for (let j = i + 1; j < mainCards.length; j++) {
            const r1 = mainCards[i].getBoundingClientRect();
            const r2 = mainCards[j].getBoundingClientRect();
            if (r1.width > 0 && r1.height > 0 && r2.width > 0 && r2.height > 0) {
                if (mainCards[i].contains(mainCards[j]) || mainCards[j].contains(mainCards[i])) continue;
                const overlapX = Math.max(0, Math.min(r1.right, r2.right) - Math.max(r1.left, r2.left));
                const overlapY = Math.max(0, Math.min(r1.bottom, r2.bottom) - Math.max(r1.top, r2.top));
                if (overlapX > 15 && overlapY > 15) {
                    overlappingSiblings.push({
                        el1: mainCards[i].className,
                        el2: mainCards[j].className,
                        overlapPx2: Math.round(overlapX * overlapY)
                    });
                }
            }
        }
    }

    const smallTouchTargets = [];
    document.querySelectorAll('button, a.btn, .nav-link, .sidebar-link, input[type="checkbox"], input[type="radio"], .theme-toggle-btn, .btn-close').forEach(el => {
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0' && rect.width > 0 && rect.height > 0) {
            if (rect.width < 44 || rect.height < 44) {
                smallTouchTargets.push({
                    tag: el.tagName.toLowerCase(),
                    text: (el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 30),
                    className: el.className,
                    width: Math.round(rect.width),
                    height: Math.round(rect.height)
                });
            }
        }
    });

    const smallFontInputs = [];
    document.querySelectorAll('input, select, textarea').forEach(el => {
        const style = window.getComputedStyle(el);
        if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
            const fontSize = parseFloat(style.fontSize);
            if (fontSize < 16 && (el.type === 'text' || el.type === 'email' || el.type === 'password' || el.tagName.toLowerCase() === 'select' || el.tagName.toLowerCase() === 'textarea')) {
                smallFontInputs.push({
                    tag: el.tagName.toLowerCase(),
                    id: el.id,
                    type: el.type,
                    fontSizePx: fontSize
                });
            }
        }
    });

    const overflowingPlaceholders = [];
    document.querySelectorAll('input[placeholder]').forEach(el => {
        const placeholder = el.getAttribute('placeholder');
        if (placeholder && placeholder.length > 0) {
            const style = window.getComputedStyle(el);
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            context.font = `${style.fontSize} ${style.fontFamily}`;
            const textMetrics = context.measureText(placeholder);
            const availableWidth = el.clientWidth - parseFloat(style.paddingLeft || 0) - parseFloat(style.paddingRight || 0) - 30;
            if (textMetrics.width > availableWidth && availableWidth > 0) {
                overflowingPlaceholders.push({
                    id: el.id,
                    placeholder: placeholder,
                    textWidth: Math.round(textMetrics.width),
                    availableWidth: Math.round(availableWidth)
                });
            }
        }
    });

    return {
        docWidth: docWidth,
        docScrollWidth: docScrollWidth,
        bodyScrollWidth: bodyScrollWidth,
        hasHorizontalOverflow: hasHorizontalOverflow,
        overflowingElements: overflowingElements.slice(0, 5),
        offscreenInteractive: offscreenInteractive.slice(0, 5),
        clippedText: clippedText.slice(0, 5),
        overlappingSiblings: overlappingSiblings.slice(0, 3),
        smallTouchTargetsCount: smallTouchTargets.length,
        smallTouchTargetsSample: smallTouchTargets.slice(0, 3),
        smallFontInputsCount: smallFontInputs.length,
        smallFontInputsSample: smallFontInputs.slice(0, 3),
        overflowingPlaceholders: overflowingPlaceholders.slice(0, 3)
    };
})();
"""

def get_all_routes():
    from app import create_app
    flask_app = create_app('testing')
    with flask_app.app_context():
        routes = []
        for rule in flask_app.url_map.iter_rules():
            if 'GET' in rule.methods and len(rule.arguments) == 0:
                routes.append(rule.rule)
        return sorted(list(set(routes)))

def login_role(context, role_name, email, password):
    page = context.new_page()
    page.goto(f"{BASE_URL}/auth/login", wait_until="domcontentloaded")
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state("domcontentloaded")
    page.close()

def run_after_audit():
    os.makedirs("docs/responsive/after", exist_ok=True)
    all_routes = get_all_routes()
    print(f"Loaded {len(all_routes)} GET routes without arguments.", flush=True)

    audit_findings = {
        "summary": {
            "total_evaluations": 0,
            "horizontal_overflow_count": 0,
            "offscreen_interactive_count": 0,
            "clipped_text_count": 0,
            "overlapping_siblings_count": 0,
            "small_touch_targets_total": 0,
            "small_font_inputs_total": 0,
            "overflowing_placeholders_count": 0,
            "http_500_count": 0
        },
        "viewport_summary": {},
        "defects_by_category": {
            "horizontal_overflow": [],
            "offscreen_interactive": [],
            "clipped_text": [],
            "overlapping_siblings": [],
            "small_touch_targets": [],
            "small_font_inputs": [],
            "overflowing_placeholders": [],
            "http_errors": [],
            "console_errors": []
        },
        "page_summary": {}
    }

    for vp in AUDIT_VIEWPORTS:
        audit_findings["viewport_summary"][vp["name"]] = {
            "evaluations": 0,
            "horizontal_overflows": 0,
            "offscreen_elements": 0,
            "clipped_texts": 0,
            "overlapping_siblings": 0,
            "small_touch_targets": 0,
            "small_font_inputs": 0,
            "overflowing_placeholders": 0
        }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        contexts = {}
        roles_config = [
            ("admin", "admin@ums.edu", "Admin@123"),
            ("teacher", "dr.tariq@ums.edu", "Teacher@123"),
            ("student", "ali.raza@ums.edu", "Student@123"),
            ("staff", "staff.kamran@ums.edu", "Staff@123"),
            ("anonymous", None, None),
        ]

        for role_name, email, pwd in roles_config:
            ctx = browser.new_context(viewport={"width": 1440, "height": 900})
            if email:
                login_role(ctx, role_name, email, pwd)
            contexts[role_name] = ctx

        # 1. Capture Full-Page AFTER Screenshots across 17 Viewports
        print("\n--- 1. Capturing Full-Page AFTER Screenshots across 17 Viewports ---", flush=True)
        for fam in REPRESENTATIVE_FAMILIES:
            role = fam["role"]
            url = fam["url"]
            fam_name = fam["family"]
            ctx = contexts[role]
            page = ctx.new_page()

            try:
                page.goto(f"{BASE_URL}{url}", timeout=15000, wait_until="domcontentloaded")
            except Exception as e:
                print(f"Error navigating to {url} as {role}: {e}", flush=True)
                page.close()
                continue

            for vp in ALL_17_VIEWPORTS:
                w, h = vp["width"], vp["height"]
                ss_path_dark = f"docs/responsive/after/{fam_name}_{w}x{h}_dark.png"
                ss_path_light = f"docs/responsive/after/{fam_name}_{w}x{h}_light.png"

                if not os.path.exists(ss_path_dark):
                    page.set_viewport_size({"width": w, "height": h})
                    page.evaluate("document.documentElement.setAttribute('data-theme', 'dark'); document.documentElement.setAttribute('data-bs-theme', 'dark');")
                    page.wait_for_timeout(20)
                    page.screenshot(path=ss_path_dark, full_page=True)

                if w in [320, 390, 768, 1024, 1440, 1920] and not os.path.exists(ss_path_light):
                    page.set_viewport_size({"width": w, "height": h})
                    page.evaluate("document.documentElement.setAttribute('data-theme', 'light'); document.documentElement.setAttribute('data-bs-theme', 'light');")
                    page.wait_for_timeout(20)
                    page.screenshot(path=ss_path_light, full_page=True)

            print(f"  [x] Captured {fam_name} across 17 viewports", flush=True)
            page.close()

        # 2. Capture Interactive States AFTER Screenshots
        print("\n--- 2. Capturing Interactive States AFTER Screenshots ---", flush=True)
        admin_ctx = contexts["admin"]

        # Drawer open states on mobile (< 1200px)
        mobile_vps = [320, 360, 390, 430, 667, 744, 768, 820, 1024]
        for w in mobile_vps:
            h = 800
            page = admin_ctx.new_page()
            page.set_viewport_size({"width": w, "height": h})
            page.goto(f"{BASE_URL}/dashboard", wait_until="domcontentloaded")
            btn = page.query_selector("[data-bs-toggle='offcanvas']")
            if btn and btn.is_visible():
                btn.click()
                page.wait_for_timeout(400)
                page.evaluate("document.documentElement.setAttribute('data-theme', 'dark'); document.documentElement.setAttribute('data-bs-theme', 'dark');")
                page.screenshot(path=f"docs/responsive/after/state_drawer_open_{w}x{h}_dark.png")
            page.close()
        print("  [x] Captured drawer open states", flush=True)

        # Modal open states
        for w in [320, 390, 768, 1024, 1440]:
            h = 900
            page = admin_ctx.new_page()
            page.set_viewport_size({"width": w, "height": h})
            page.goto(f"{BASE_URL}/admin/users", wait_until="domcontentloaded")
            del_btn = page.query_selector("button[data-bs-toggle='modal']")
            if del_btn and del_btn.is_visible():
                del_btn.click()
                page.wait_for_timeout(350)
                page.evaluate("document.documentElement.setAttribute('data-theme', 'dark'); document.documentElement.setAttribute('data-bs-theme', 'dark');")
                page.screenshot(path=f"docs/responsive/after/state_modal_open_{w}x{h}_dark.png")
            page.close()
        print("  [x] Captured modal open states", flush=True)

        # 3. Running Metric Audit
        print("\n--- 3. Running Metric Audit across Routes & Viewports ---", flush=True)
        total_evaluations = 0

        for role_name, email, _ in roles_config:
            ctx = contexts[role_name]
            page = ctx.new_page()
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            # Test all routes for this role
            for r in all_routes:
                page_key = f"{role_name}:{r}"
                if page_key not in audit_findings["page_summary"]:
                    audit_findings["page_summary"][page_key] = {"evaluations": 0, "violations": 0}

                # We evaluate key representative viewports across dark & light themes
                for vp in AUDIT_VIEWPORTS:
                    vp_key = vp["name"]
                    page.set_viewport_size({"width": vp["width"], "height": vp["height"]})

                    for theme in ["dark", "light"]:
                        total_evaluations += 1
                        audit_findings["summary"]["total_evaluations"] += 1
                        audit_findings["viewport_summary"][vp_key]["evaluations"] += 1
                        audit_findings["page_summary"][page_key]["evaluations"] += 1

                        url = f"{BASE_URL}{r}"
                        try:
                            response = page.goto(url, timeout=12000, wait_until="domcontentloaded")
                            status = response.status if response else 0
                        except Exception as e:
                            status = 0

                        if status >= 500:
                            audit_findings["summary"]["http_500_count"] += 1
                            audit_findings["defects_by_category"]["http_errors"].append({
                                "role": role_name, "route": r, "status": status, "viewport": vp["name"], "theme": theme
                            })
                            continue
                        elif status in [401, 403, 302, 404]:
                            pass

                        page.evaluate(f"document.documentElement.setAttribute('data-theme', '{theme}'); document.documentElement.setAttribute('data-bs-theme', '{theme}');")
                        page.wait_for_timeout(10)

                        res = page.evaluate(AUDIT_JS)

                        if res["hasHorizontalOverflow"]:
                            audit_findings["summary"]["horizontal_overflow_count"] += 1
                            audit_findings["viewport_summary"][vp_key]["horizontal_overflows"] += 1
                            audit_findings["defects_by_category"]["horizontal_overflow"].append({
                                "role": role_name, "route": r, "viewport": vp["name"], "theme": theme,
                                "overflowPx": res["docScrollWidth"] - res["docWidth"],
                                "elements": res["overflowingElements"]
                            })
                            audit_findings["page_summary"][page_key]["violations"] += 1

                        if res["offscreenInteractive"]:
                            audit_findings["summary"]["offscreen_interactive_count"] += len(res["offscreenInteractive"])
                            audit_findings["viewport_summary"][vp_key]["offscreen_elements"] += len(res["offscreenInteractive"])
                            audit_findings["defects_by_category"]["offscreen_interactive"].append({
                                "role": role_name, "route": r, "viewport": vp["name"], "theme": theme,
                                "elements": res["offscreenInteractive"]
                            })
                            audit_findings["page_summary"][page_key]["violations"] += len(res["offscreenInteractive"])

                        if res["smallFontInputsCount"] > 0 and vp["width"] < 768:
                            audit_findings["defects_by_category"]["small_font_inputs"].append({
                                "role": role_name, "route": r, "viewport": vp["name"], "theme": theme,
                                "count": res["smallFontInputsCount"],
                                "samples": res["smallFontInputsSample"]
                            })
                            audit_findings["viewport_summary"][vp_key]["small_font_inputs"] += res["smallFontInputsCount"]

            page.close()

        for ctx in contexts.values():
            ctx.close()
        browser.close()

    print(f"\nAfter-Audit complete! Evaluated {total_evaluations} checks.", flush=True)
    with open("tests/responsive/audit_after.json", "w", encoding="utf-8") as f:
        json.dump(audit_findings, f, indent=2)
    print("Saved results to tests/responsive/audit_after.json", flush=True)

if __name__ == "__main__":
    run_after_audit()
