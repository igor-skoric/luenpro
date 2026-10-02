/**
 * Luen Pro — smooth scroll & active nav
 */
(function () {
    'use strict';

    const HEADER_OFFSET = 16;

    function getHeaderHeight() {
        const header = document.querySelector('.site-header');
        return header ? header.offsetHeight + HEADER_OFFSET : HEADER_OFFSET;
    }

    function scrollToSection(id, updateHash) {
        const target = document.getElementById(id);
        if (!target) return false;

        const top = target.getBoundingClientRect().top + window.scrollY - getHeaderHeight();
        window.scrollTo({ top, behavior: 'smooth' });

        if (updateHash !== false) {
            history.pushState(null, '', `#${id}`);
        }

        return true;
    }

    function handleAnchorClick(event) {
        const link = event.target.closest('a[href*="#"]');
        if (!link) return;

        const url = new URL(link.href, window.location.origin);
        const hash = url.hash.replace('#', '');
        if (!hash) return;

        const onHomePage = url.pathname === window.location.pathname;
        if (!onHomePage) return;

        if (!document.getElementById(hash)) return;

        event.preventDefault();
        scrollToSection(hash);
    }

    function scrollOnLoad() {
        const hash = window.location.hash.replace('#', '');
        if (!hash || !document.getElementById(hash)) return;

        setTimeout(function () {
            scrollToSection(hash, false);
        }, 100);
    }

    function initActiveNav() {
        const navLinks = document.querySelectorAll('[data-nav]');
        if (!navLinks.length) return;

        const sections = Array.from(navLinks)
            .map(function (link) {
                return document.getElementById(link.dataset.nav);
            })
            .filter(Boolean);

        if (!sections.length) return;

        const observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;
                    const id = entry.target.id;
                    navLinks.forEach(function (link) {
                        link.classList.toggle('is-active', link.dataset.nav === id);
                    });
                });
            },
            {
                rootMargin: `-${getHeaderHeight()}px 0px -55% 0px`,
                threshold: 0,
            }
        );

        sections.forEach(function (section) {
            observer.observe(section);
        });
    }

    document.addEventListener('click', handleAnchorClick);
    document.addEventListener('DOMContentLoaded', function () {
        document.documentElement.classList.add('js-ready');
        scrollOnLoad();
        initActiveNav();
    });
})();
