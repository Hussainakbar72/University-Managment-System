/**
 * APP.JS - University Management System
 * Theme Toggle, Sidebar Collapse State, Auto-Dismiss Toasts, UI Utilities
 */

(function () {
  'use strict';

  // -------------------------------------------------------------------------
  // 1. Theme Management (Bootstrap 5.3 data-bs-theme with localStorage)
  // -------------------------------------------------------------------------
  const THEME_STORAGE_KEY = 'ums-color-theme';

  function getPreferredTheme() {
    const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    if (storedTheme) {
      return storedTheme;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    document.body.setAttribute('data-bs-theme', theme);

    // Update all theme toggle buttons on the page
    document.querySelectorAll('.theme-toggle-btn').forEach((btn) => {
      const icon = btn.querySelector('i');
      if (icon) {
        if (theme === 'dark') {
          icon.className = 'bi bi-sun-fill text-warning';
          btn.setAttribute('title', 'Switch to Light Mode');
          btn.setAttribute('aria-label', 'Switch to Light Mode');
        } else {
          icon.className = 'bi bi-moon-stars-fill text-indigo';
          btn.setAttribute('title', 'Switch to Dark Mode');
          btn.setAttribute('aria-label', 'Switch to Dark Mode');
        }
      }
    });
  }

  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    localStorage.setItem(THEME_STORAGE_KEY, newTheme);
    applyTheme(newTheme);
  }

  // Apply immediately upon script execution
  applyTheme(getPreferredTheme());

  // Listen for OS theme preference changes if user hasn't explicitly set a preference
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem(THEME_STORAGE_KEY)) {
      applyTheme(e.matches ? 'dark' : 'light');
    }
  });

  // -------------------------------------------------------------------------
  // 2. DOM Ready Initializations
  // -------------------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', () => {
    // Re-verify theme icons
    applyTheme(getPreferredTheme());

    // Attach theme toggle button listeners
    document.querySelectorAll('.theme-toggle-btn').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        toggleTheme();
      });
    });

    // -----------------------------------------------------------------------
    // 3. Auto-Dismiss Glass Toasts (~5 seconds)
    // -----------------------------------------------------------------------
    document.querySelectorAll('.glass-toast').forEach((toast) => {
      const closeBtn = toast.querySelector('.toast-close');
      if (closeBtn) {
        closeBtn.addEventListener('click', () => {
          dismissToast(toast);
        });
      }

      // Auto-dismiss after 5s
      setTimeout(() => {
        dismissToast(toast);
      }, 5000);
    });

    function dismissToast(toast) {
      if (!toast) return;
      toast.style.transition = 'opacity 300ms ease, transform 300ms ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px)';
      setTimeout(() => {
        toast.remove();
      }, 300);
    }

    // -----------------------------------------------------------------------
    // 4. Search Clear Button Helper
    // -----------------------------------------------------------------------
    document.querySelectorAll('.search-wrapper').forEach((wrapper) => {
      const input = wrapper.querySelector('.glass-input');
      const clearBtn = wrapper.querySelector('.btn-clear-search');
      if (input && clearBtn) {
        const updateClearVisibility = () => {
          clearBtn.style.display = input.value.trim().length > 0 ? 'block' : 'none';
        };

        updateClearVisibility();
        input.addEventListener('input', updateClearVisibility);

        clearBtn.addEventListener('click', (e) => {
          e.preventDefault();
          input.value = '';
          updateClearVisibility();
          input.focus();
          // If within a form, submit or trigger search
          const form = wrapper.closest('form');
          if (form) {
            form.submit();
          }
        });
      }
    });

    // -----------------------------------------------------------------------
    // 5. Sidebar Collapsible Group State Persistence & Mobile Rules
    // -----------------------------------------------------------------------
    const COLLAPSE_STORAGE_PREFIX = 'ums-nav-collapse-';
    const isMobileWidth = () => window.innerWidth < 1200;

    document.querySelectorAll('.nav-group-collapse').forEach((collapseEl) => {
      const id = collapseEl.getAttribute('id');
      if (!id) return;

      const isStoredClosed = localStorage.getItem(COLLAPSE_STORAGE_PREFIX + id) === 'closed';
      const bsCollapse = bootstrap.Collapse.getOrCreateInstance(collapseEl, {
        toggle: false
      });

      // If active link is inside this collapse, always keep it open
      const hasActiveChild = collapseEl.querySelector('.active-menu, .active');
      if (hasActiveChild) {
        bsCollapse.show();
        localStorage.setItem(COLLAPSE_STORAGE_PREFIX + id, 'open');
      } else if (isMobileWidth() || isStoredClosed) {
        // On mobile, start collapsed unless active
        bsCollapse.hide();
      }

      collapseEl.addEventListener('hidden.bs.collapse', () => {
        if (!isMobileWidth()) {
          localStorage.setItem(COLLAPSE_STORAGE_PREFIX + id, 'closed');
        }
        const trigger = document.querySelector(`[data-bs-target="#${id}"]`);
        if (trigger) trigger.setAttribute('aria-expanded', 'false');
      });

      collapseEl.addEventListener('shown.bs.collapse', () => {
        if (!isMobileWidth()) {
          localStorage.setItem(COLLAPSE_STORAGE_PREFIX + id, 'open');
        }
        const trigger = document.querySelector(`[data-bs-target="#${id}"]`);
        if (trigger) trigger.setAttribute('aria-expanded', 'true');
      });
    });

    // -----------------------------------------------------------------------
    // 5b. Mobile Offcanvas Behavior (Focus, Auto-Dismiss, Body Scroll)
    // -----------------------------------------------------------------------
    const offcanvasEl = document.getElementById('sidebarOffcanvas');
    if (offcanvasEl) {
      const hamburgerBtn = document.querySelector("[data-bs-target='#sidebarOffcanvas']");

      // Close offcanvas drawer when a navigation link is clicked
      offcanvasEl.querySelectorAll('.sidebar-link').forEach((link) => {
        link.addEventListener('click', () => {
          const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasEl);
          if (bsOffcanvas) {
            bsOffcanvas.hide();
          }
        });
      });

      // Return focus to hamburger button when offcanvas closes
      offcanvasEl.addEventListener('hidden.bs.offcanvas', () => {
        if (hamburgerBtn) {
          hamburgerBtn.focus();
        }
      });
    }

    // -----------------------------------------------------------------------
    // 5c. Sidebar Live Search Filter
    // -----------------------------------------------------------------------
    document.querySelectorAll('.sidebar-search-input').forEach((searchInput) => {
      const sidebarContainer = searchInput.closest('.sidebar-scrollable') || searchInput.closest('aside') || searchInput.closest('.offcanvas');
      if (!sidebarContainer) return;

      searchInput.addEventListener('input', () => {
        const query = searchInput.value.trim().toLowerCase();
        const links = sidebarContainer.querySelectorAll('.sidebar-link');
        const groups = sidebarContainer.querySelectorAll('.nav-group-collapse');
        const headers = sidebarContainer.querySelectorAll('.nav-group-header');

        if (!query) {
          // Restore normal visibility
          links.forEach((link) => (link.style.display = ''));
          headers.forEach((h) => (h.style.display = ''));
          groups.forEach((group) => {
            const hasActive = group.querySelector('.active-menu, .active');
            const bsCollapse = bootstrap.Collapse.getInstance(group);
            if (bsCollapse) {
              if (hasActive) bsCollapse.show();
              else if (isMobileWidth()) bsCollapse.hide();
            }
          });
          return;
        }

        // Filter links
        links.forEach((link) => {
          const text = link.textContent.toLowerCase();
          const match = text.includes(query);
          link.style.display = match ? 'flex' : 'none';

          if (match) {
            const parentCollapse = link.closest('.nav-group-collapse');
            if (parentCollapse) {
              const bsCollapse = bootstrap.Collapse.getOrCreateInstance(parentCollapse, { toggle: false });
              bsCollapse.show();
            }
          }
        });

        // Hide headers if no visible links inside
        groups.forEach((group) => {
          const id = group.getAttribute('id');
          const header = sidebarContainer.querySelector(`[data-bs-target="#${id}"]`);
          const visibleLinks = group.querySelectorAll(".sidebar-link:not([style*='display: none'])");
          if (header) {
            header.style.display = visibleLinks.length > 0 ? '' : 'none';
          }
        });
      });
    });

    // -----------------------------------------------------------------------
    // 6. Password Show / Hide Toggle Helper
    // -----------------------------------------------------------------------
    document.querySelectorAll('.password-toggle-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-target');
        const input = document.getElementById(targetId);
        const icon = btn.querySelector('i');
        if (input) {
          if (input.type === 'password') {
            input.type = 'text';
            if (icon) icon.className = 'bi bi-eye-slash';
          } else {
            input.type = 'password';
            if (icon) icon.className = 'bi bi-eye';
          }
        }
      });
    });
  });
})();
