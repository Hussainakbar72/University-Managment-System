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
() => {
    const docWidth = window.innerWidth;
    const docHeight = window.innerHeight;
    const scrollWidth = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth);
    const hasHorizontalOverflow = scrollWidth > docWidth + 1;

    const isInsideScrollContainer = (el) => {
        let parent = el.parentElement;
        while (parent && parent !== document.body && parent !== document.documentElement) {
            const style = window.getComputedStyle(parent);
            if (['auto', 'scroll'].includes(style.overflowX)) {
                return true;
            }
            parent = parent.parentElement;
        }
        return false;
    };

    const getSelector = (el) => {
        if (!el || !el.tagName) return 'unknown';
        if (el.id) return '#' + el.id;
        let sel = el.tagName.toLowerCase();
        if (el.className && typeof el.className === 'string') {
            const classes = el.className.trim().split(/\\s+/).filter(c => c && !c.includes(':') && !c.includes('[')).slice(0, 2);
            if (classes.length) sel += '.' + classes.join('.');
        }
        return sel;
    };

    const offscreenElements = [];
    const clippedText = [];
    const allElements = document.querySelectorAll('body *');

    allElements.forEach(el => {
        if (el.offsetWidth === 0 && el.offsetHeight === 0) return;
        const rect = el.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
            if (rect.right > docWidth + 1) {
                if (!isInsideScrollContainer(el)) {
                    offscreenElements.push({
                        selector: getSelector(el),
                        right: Math.round(rect.right),
                        docWidth: docWidth,
                        overflowPx: Math.round(rect.right - docWidth)
                    });
                }
            }
        }

        if (el.children.length === 0 && el.textContent.trim().length > 0) {
            const style = window.getComputedStyle(el);
            if (['hidden', 'clip'].includes(style.overflow) || ['hidden', 'clip'].includes(style.overflowX)) {
                if (style.textOverflow !== 'ellipsis' && el.scrollWidth > el.clientWidth + 2) {
                    clippedText.push({
                        selector: getSelector(el),
                        text: el.textContent.trim().slice(0, 25),
                        scrollWidth: el.scrollWidth,
                        clientWidth: el.clientWidth
                    });
                }
            }
        }
    });

    const overlappingSiblings = [];
    const headerContainers = document.querySelectorAll('.glass-topbar, .topbar-wrapper, .page-header, header, .user-chip, [class*="justify-content-between"]');
    headerContainers.forEach(container => {
        const children = Array.from(container.children).filter(c => {
            const r = c.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
        });
        for (let i = 0; i < children.length; i++) {
            for (let j = i + 1; j < children.length; j++) {
                const r1 = children[i].getBoundingClientRect();
                const r2 = children[j].getBoundingClientRect();
                const overlapX = Math.max(0, Math.min(r1.right, r2.right) - Math.max(r1.left, r2.left));
                const overlapY = Math.max(0, Math.min(r1.bottom, r2.bottom) - Math.max(r1.top, r2.top));
                if (overlapX > 2 && overlapY > 2) {
                    overlappingSiblings.push({
                        container: getSelector(container),
                        el1: getSelector(children[i]),
                        el2: getSelector(children[j]),
                        overlapArea: Math.round(overlapX * overlapY)
                    });
                }
            }
        }
    });

    const smallTouchTargets = [];
    const isTouchViewport = docWidth <= 1024;
    if (isTouchViewport) {
        const interactives = document.querySelectorAll('button, a, input, select, textarea, [role="button"], .btn');
        interactives.forEach(el => {
            if (el.offsetParent === null) return;
            const rect = el.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                if (rect.width < 43 || rect.height < 43) {
                    smallTouchTargets.push({
                        selector: getSelector(el),
                        label: (el.textContent || el.title || el.getAttribute('aria-label') || '').trim().slice(0, 20),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height)
                    });
                }
            }
        });
    }

    const smallFontInputs = [];
    if (docWidth <= 767) {
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(el => {
            if (['hidden', 'checkbox', 'radio'].includes(el.type)) return;
            if (el.offsetParent === null) return;
            const style = window.getComputedStyle(el);
            const fs = parseFloat(style.fontSize);
            if (fs < 15.5) {
                smallFontInputs.push({
                    selector: getSelector(el),
                    fontSize: fs
                });
            }
        });
    }

    const overflowingPlaceholders = [];
    const inputsWithPlaceholder = document.querySelectorAll('input[placeholder], textarea[placeholder]');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    inputsWithPlaceholder.forEach(el => {
        const ph = el.getAttribute('placeholder');
        if (ph && el.clientWidth > 0 && el.offsetParent !== null) {
            const style = window.getComputedStyle(el);
            ctx.font = `${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
            const textWidth = ctx.measureText(ph).width;
            const padding = parseFloat(style.paddingLeft || 0) + parseFloat(style.paddingRight || 0);
            const availableWidth = el.clientWidth - padding;
            if (textWidth > availableWidth + 4) {
                overflowingPlaceholders.push({
                    selector: getSelector(el),
                    placeholder: ph,
                    textWidth: Math.round(textWidth),
                    availableWidth: Math.round(availableWidth)
                });
            }
        }
    });

    return {
        docWidth: docWidth,
        docHeight: docHeight,
        scrollWidth: Math.round(scrollWidth),
        hasHorizontalOverflow: hasHorizontalOverflow,
        overflowDelta: Math.max(0, Math.round(scrollWidth - docWidth)),
        offscreenElements: offscreenElements.slice(0, 5),
        clippedText: clippedText.slice(0, 5),
        overlappingSiblings: overlappingSiblings.slice(0, 5),
        smallTouchTargetsCount: smallTouchTargets.length,
        smallTouchTargetsSample: smallTouchTargets.slice(0, 4),
        smallFontInputsCount: smallFontInputs.length,
        smallFontInputsSample: smallFontInputs.slice(0, 4),
        overflowingPlaceholders: overflowingPlaceholders.slice(0, 4)
    };
}
"""

def login_role(context, role, email, password):
    page = context.new_page()
    page.goto(f"{BASE_URL}/auth/login", wait_until="domcontentloaded")
    page.fill("input[name='email']", email)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")
    page.wait_for_url(f"{BASE_URL}/dashboard")
    page.close()
    print(f"Logged in as {role} ({email})", flush=True)

def collect_routes_from_test_client():
    from app import create_app
    from app.models.auth import User

    app = create_app('testing')  # Use testing config so DB is not locked
    routes = []
    for rule in app.url_map.iter_rules():
        if 'GET' in rule.methods and '<' not in rule.rule and not rule.rule.startswith('/static'):
            routes.append(rule.rule)
    routes = sorted(list(set(routes)))

    roles = [
        ("admin", "admin@ums.edu"),
        ("teacher", "dr.tariq@ums.edu"),
        ("student", "ali.raza@ums.edu"),
        ("staff", "staff.kamran@ums.edu"),
        ("anonymous", None),
    ]

    dev_app = create_app('development')
    user_ids = {}
    with dev_app.app_context():
        for role_name, email in roles:
            if email:
                u = User.query.filter_by(email=email).first()
                if u:
                    user_ids[role_name] = str(u.id)

    routes_per_role = {}
    for role_name, email in roles:
        r200 = []
        uid = user_ids.get(role_name)
        for r in routes:
            client = dev_app.test_client()
            if uid:
                with client.session_transaction() as sess:
                    sess['_user_id'] = uid
                    sess['_fresh'] = True
            res = client.get(r, follow_redirects=False)
            if res.status_code == 200:
                r200.append(r)
        routes_per_role[role_name] = r200
        print(f"Role {role_name}: {len(r200)} status 200 routes", flush=True)

    return routes_per_role

def run_audit():
    print("--- 1. Computing 200 routes per role ---", flush=True)
    routes_per_role = collect_routes_from_test_client()

    audit_findings = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_role_routes_200": sum(len(r) for r in routes_per_role.values()),
        "defects_by_category": {
            "horizontal_overflow": [],
            "offscreen_elements": [],
            "clipped_text": [],
            "overlapping_siblings": [],
            "small_touch_targets": [],
            "small_font_inputs": [],
            "overflowing_placeholders": [],
            "console_errors": []
        },
        "page_summary": {},
        "viewport_summary": {}
    }

    os.makedirs("docs/responsive/before", exist_ok=True)

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

        print("\n--- 2. Capturing Full-Page BEFORE Screenshots across 17 Viewports ---", flush=True)
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
                ss_path_dark = f"docs/responsive/before/{fam_name}_{w}x{h}_dark.png"
                ss_path_light = f"docs/responsive/before/{fam_name}_{w}x{h}_light.png"

                if not os.path.exists(ss_path_dark):
                    page.set_viewport_size({"width": w, "height": h})
                    page.evaluate("document.documentElement.setAttribute('data-bs-theme', 'dark')")
                    page.wait_for_timeout(20)
                    page.screenshot(path=ss_path_dark, full_page=True)

                if w in [320, 390, 768, 1024, 1440, 1920] and not os.path.exists(ss_path_light):
                    page.set_viewport_size({"width": w, "height": h})
                    page.evaluate("document.documentElement.setAttribute('data-bs-theme', 'light')")
                    page.wait_for_timeout(20)
                    page.screenshot(path=ss_path_light, full_page=True)

            print(f"  [x] Captured {fam_name} across 17 viewports", flush=True)
            page.close()

        # Capture interactive states: drawer open and delete modal open
        print("\n--- 2b. Capturing Interactive States BEFORE Screenshots ---", flush=True)
        admin_ctx = contexts["admin"]
        
        # State: Mobile Drawer Open on mobile viewports (< 1200px)
        mobile_vps = [320, 360, 390, 430, 667, 744, 768, 820, 1024]
        for w in mobile_vps:
            h = 800
            page = admin_ctx.new_page()
            page.set_viewport_size({"width": w, "height": h})
            page.goto(f"{BASE_URL}/dashboard", wait_until="domcontentloaded")
            btn = page.query_selector("[data-bs-toggle='offcanvas']")
            if btn and btn.is_visible():
                btn.click()
                page.wait_for_timeout(350)
                page.evaluate("document.documentElement.setAttribute('data-bs-theme', 'dark')")
                page.screenshot(path=f"docs/responsive/before/state_drawer_open_{w}x{h}_dark.png", full_page=True)
            else:
                print(f"  [INFO] Drawer toggle button not visible at {w}px (d-lg-none hides it >= 992px)", flush=True)
            page.close()
        print("  [x] Captured drawer open states", flush=True)

        # State: Delete Modal Open
        for w in [320, 390, 768, 1024, 1440]:
            h = 900
            page = admin_ctx.new_page()
            page.set_viewport_size({"width": w, "height": h})
            page.goto(f"{BASE_URL}/admin/users", wait_until="domcontentloaded")
            del_btn = page.query_selector("button[data-bs-toggle='modal']")
            if del_btn and del_btn.is_visible():
                del_btn.click()
                page.wait_for_timeout(350)
                page.evaluate("document.documentElement.setAttribute('data-bs-theme', 'dark')")
                page.screenshot(path=f"docs/responsive/before/state_modal_open_{w}x{h}_dark.png", full_page=True)
            page.close()
        print("  [x] Captured modal open states", flush=True)

        print("\n--- 3. Running Metric Audit on Routes across 8 Viewports & 2 Themes ---", flush=True)
        total_evaluations = 0

        for role_name, email, _ in roles_config:
            ctx = contexts[role_name]
            routes = routes_per_role[role_name]
            print(f"Auditing role {role_name} ({len(routes)} routes)...", flush=True)

            page = ctx.new_page()
            console_errors = []
            page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda err: console_errors.append(str(err)))

            for r_idx, r in enumerate(routes):
                if r_idx % 15 == 0 or r_idx == len(routes) - 1:
                    print(f"  [{role_name}] Auditing route {r_idx+1}/{len(routes)}: {r}", flush=True)
                try:
                    page.goto(f"{BASE_URL}{r}", timeout=10000, wait_until="domcontentloaded")
                except Exception as e:
                    continue

                for vp in AUDIT_VIEWPORTS:
                    w, h = vp["width"], vp["height"]
                    page.set_viewport_size({"width": w, "height": h})

                    for theme in ["dark", "light"]:
                        page.evaluate(f"document.documentElement.setAttribute('data-bs-theme', '{theme}')")
                        res = page.evaluate(AUDIT_JS)
                        total_evaluations += 1

                        page_key = f"{role_name}:{r}"
                        if page_key not in audit_findings["page_summary"]:
                            audit_findings["page_summary"][page_key] = {
                                "role": role_name,
                                "route": r,
                                "violations": 0,
                                "details": []
                            }

                        vp_key = f"{w}x{h}_{theme}"
                        if vp_key not in audit_findings["viewport_summary"]:
                            audit_findings["viewport_summary"][vp_key] = {
                                "horizontal_overflows": 0,
                                "offscreen_elements": 0,
                                "clipped_texts": 0,
                                "overlapping_siblings": 0,
                                "small_touch_targets": 0,
                                "small_font_inputs": 0,
                                "overflowing_placeholders": 0
                            }

                        if res["hasHorizontalOverflow"]:
                            audit_findings["defects_by_category"]["horizontal_overflow"].append({
                                "role": role_name, "route": r, "viewport": vp["name"], "theme": theme,
                                "scrollWidth": res["scrollWidth"], "docWidth": res["docWidth"],
                                "delta": res["overflowDelta"]
                            })
                            audit_findings["page_summary"][page_key]["violations"] += 1
                            audit_findings["viewport_summary"][vp_key]["horizontal_overflows"] += 1

                        if res["offscreenElements"]:
                            audit_findings["defects_by_category"]["offscreen_elements"].append({
                                "role": role_name, "route": r, "viewport": vp["name"], "theme": theme,
                                "elements": res["offscreenElements"]
                            })
                            audit_findings["page_summary"][page_key]["violations"] += len(res["offscreenElements"])
                            audit_findings["viewport_summary"][vp_key]["offscreen_elements"] += len(res["offscreenElements"])

                        if res["clippedText"]:
                            audit_findings["defects_by_category"]["clipped_text"].append({
                                "role": role_name, "route": r, "viewport": vp["name"], "theme": theme,
                                "samples": res["clippedText"]
                            })
                            audit_findings["page_summary"][page_key]["violations"] += len(res["clippedText"])
                            audit_findings["viewport_summary"][vp_key]["clipped_texts"] += len(res["clippedText"])

                        if res["overlappingSiblings"]:
                            audit_findings["defects_by_category"]["overlapping_siblings"].append({
                                "role": role_name, "route": r, "viewport": vp["name"], "theme": theme,
                                "overlaps": res["overlappingSiblings"]
                            })
                            audit_findings["page_summary"][page_key]["violations"] += len(res["overlappingSiblings"])
                            audit_findings["viewport_summary"][vp_key]["overlapping_siblings"] += len(res["overlappingSiblings"])

                        if res["smallTouchTargetsCount"] > 0:
                            audit_findings["defects_by_category"]["small_touch_targets"].append({
                                "role": role_name, "route": r, "viewport": vp["name"], "theme": theme,
                                "count": res["smallTouchTargetsCount"],
                                "samples": res["smallTouchTargetsSample"]
                            })
                            audit_findings["viewport_summary"][vp_key]["small_touch_targets"] += res["smallTouchTargetsCount"]

                        if res["smallFontInputsCount"] > 0:
                            audit_findings["defects_by_category"]["small_font_inputs"].append({
                                "role": role_name, "route": r, "viewport": vp["name"], "theme": theme,
                                "count": res["smallFontInputsCount"],
                                "samples": res["smallFontInputsSample"]
                            })
                            audit_findings["viewport_summary"][vp_key]["small_font_inputs"] += res["smallFontInputsCount"]

                        if res["overflowingPlaceholders"]:
                            audit_findings["defects_by_category"]["overflowing_placeholders"].append({
                                "role": role_name, "route": r, "viewport": vp["name"], "theme": theme,
                                "placeholders": res["overflowingPlaceholders"]
                            })
                            audit_findings["page_summary"][page_key]["violations"] += len(res["overflowingPlaceholders"])
                            audit_findings["viewport_summary"][vp_key]["overflowing_placeholders"] += len(res["overflowingPlaceholders"])

                if console_errors:
                    audit_findings["defects_by_category"]["console_errors"].append({
                        "role": role_name, "route": r, "errors": list(set(console_errors))
                    })
                    console_errors.clear()

            page.close()

        for ctx in contexts.values():
            ctx.close()
        browser.close()

    print(f"\nAudit complete! Evaluated {total_evaluations} checks.", flush=True)
    with open("tests/responsive/audit_results.json", "w", encoding="utf-8") as f:
        json.dump(audit_findings, f, indent=2)
    print("Saved results to tests/responsive/audit_results.json", flush=True)

if __name__ == "__main__":
    run_audit()
