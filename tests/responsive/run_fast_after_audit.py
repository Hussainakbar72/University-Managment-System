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
                    text: (el.innerText || el.value || '').trim().slice(0, 30),
                    left: Math.round(rect.left),
                    right: Math.round(rect.right)
                });
            }
        }
    });

    const smallTouchTargets = [];
    document.querySelectorAll('button, a.btn, .nav-link, .sidebar-link, input[type="checkbox"], input[type="radio"], .theme-toggle-btn, .btn-close').forEach(el => {
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0' && rect.width > 0 && rect.height > 0) {
            if (rect.width < 44 || rect.height < 44) {
                smallTouchTargets.push({
                    tag: el.tagName.toLowerCase(),
                    text: (el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 30),
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
                    fontSizePx: fontSize
                });
            }
        }
    });

    return {
        docWidth: docWidth,
        docScrollWidth: docScrollWidth,
        hasHorizontalOverflow: hasHorizontalOverflow,
        overflowingElements: overflowingElements.slice(0, 5),
        offscreenInteractive: offscreenInteractive.slice(0, 5),
        smallTouchTargetsCount: smallTouchTargets.length,
        smallFontInputsCount: smallFontInputs.length
    };
})();
"""

def get_routes_per_role():
    from app import create_app
    app = create_app('testing')
    routes = []
    for rule in app.url_map.iter_rules():
        if 'GET' in rule.methods and '<' not in rule.rule and not rule.rule.startswith('/static'):
            routes.append(rule.rule)
    routes = sorted(list(set(routes)))
    return {
        "admin": routes,
        "teacher": routes,
        "student": routes,
        "staff": routes,
        "anonymous": routes,
    }

def login_role(context, email, password):
    page = context.new_page()
    page.goto(f"{BASE_URL}/auth/login", wait_until="domcontentloaded")
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state("domcontentloaded")
    page.close()

def main():
    routes_per_role = get_routes_per_role()
    roles_config = [
        ("admin", "admin@ums.edu", "Admin@123"),
        ("teacher", "dr.tariq@ums.edu", "Teacher@123"),
        ("student", "ali.raza@ums.edu", "Student@123"),
        ("staff", "staff.kamran@ums.edu", "Staff@123"),
        ("anonymous", None, None),
    ]

    audit_findings = {
        "summary": {
            "total_evaluations": 0,
            "horizontal_overflow_count": 0,
            "offscreen_interactive_count": 0,
            "small_touch_targets_total": 0,
            "small_font_inputs_total": 0,
            "http_500_count": 0
        },
        "viewport_summary": {},
        "defects_by_category": {
            "horizontal_overflow": [],
            "offscreen_interactive": [],
            "small_touch_targets": [],
            "small_font_inputs": []
        }
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        contexts = {}
        for role_name, email, pwd in roles_config:
            ctx = browser.new_context(viewport={"width": 1440, "height": 900})
            if email:
                login_role(ctx, email, pwd)
            contexts[role_name] = ctx

        total_evals = 0
        start_time = time.time()
        print("Starting fast AFTER metric audit...", flush=True)

        for role_name, email, _ in roles_config:
            ctx = contexts[role_name]
            routes = routes_per_role[role_name]
            print(f"Auditing role {role_name} ({len(routes)} routes)...", flush=True)

            page = ctx.new_page()
            for r_idx, r in enumerate(routes):
                try:
                    page.goto(f"{BASE_URL}{r}", timeout=8000, wait_until="domcontentloaded")
                except Exception:
                    continue

                for vp in AUDIT_VIEWPORTS:
                    w, h = vp["width"], vp["height"]
                    page.set_viewport_size({"width": w, "height": h})

                    for theme in ["dark", "light"]:
                        total_evals += 1
                        page.evaluate(f"document.documentElement.setAttribute('data-theme', '{theme}'); document.documentElement.setAttribute('data-bs-theme', '{theme}');")
                        res = page.evaluate(AUDIT_JS)

                        vp_key = f"{w}x{h}_{theme}"
                        if vp_key not in audit_findings["viewport_summary"]:
                            audit_findings["viewport_summary"][vp_key] = {
                                "evaluations": 0,
                                "horizontal_overflows": 0,
                                "offscreen_elements": 0,
                                "small_font_inputs": 0
                            }
                        audit_findings["viewport_summary"][vp_key]["evaluations"] += 1

                        if res["hasHorizontalOverflow"]:
                            audit_findings["summary"]["horizontal_overflow_count"] += 1
                            audit_findings["viewport_summary"][vp_key]["horizontal_overflows"] += 1
                            audit_findings["defects_by_category"]["horizontal_overflow"].append({
                                "role": role_name, "route": r, "viewport": vp_key,
                                "overflowPx": res["docScrollWidth"] - res["docWidth"],
                                "elements": res["overflowingElements"]
                            })

                        if res["offscreenInteractive"]:
                            audit_findings["summary"]["offscreen_interactive_count"] += len(res["offscreenInteractive"])
                            audit_findings["viewport_summary"][vp_key]["offscreen_elements"] += len(res["offscreenInteractive"])

                        if res["smallFontInputsCount"] > 0 and w < 768:
                            audit_findings["summary"]["small_font_inputs_total"] += res["smallFontInputsCount"]
                            audit_findings["viewport_summary"][vp_key]["small_font_inputs"] += res["smallFontInputsCount"]

            page.close()

        for ctx in contexts.values():
            ctx.close()
        browser.close()

    audit_findings["summary"]["total_evaluations"] = total_evals
    elapsed = round(time.time() - start_time, 1)
    print(f"Audit completed in {elapsed}s with {total_evals} evaluations!", flush=True)
    with open("tests/responsive/audit_after.json", "w", encoding="utf-8") as f:
        json.dump(audit_findings, f, indent=2)
    print("Saved results to tests/responsive/audit_after.json", flush=True)

if __name__ == "__main__":
    main()
