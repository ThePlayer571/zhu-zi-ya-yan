<template>
  <footer class="site-footer">
    <div class="footer-content">
      <div class="footer-links">
        <a
          href="https://github.com/ThePlayer571/zhu-zi-ya-yan"
          target="_blank"
          rel="noopener noreferrer"
          class="footer-link"
        >
          <svg viewBox="0 0 24 24" width="18" height="18" class="link-icon">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" fill="currentColor" />
          </svg>
          项目 GitHub
        </a>
        <span class="footer-divider">|</span>
        <a
          href="https://github.com/ThePlayer571"
          target="_blank"
          rel="noopener noreferrer"
          class="footer-link"
        >
          作者 GitHub
        </a>
        <span class="footer-divider">|</span>
        <a
          href="https://space.bilibili.com/260468462"
          target="_blank"
          rel="noopener noreferrer"
          class="footer-link"
        >
          B 站主页
        </a>
      </div>
      <p class="footer-copy">
        © 诸子雅言 · 春秋之风，代码之美
      </p>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  padding: var(--space-2xl) var(--space-lg);
  background: var(--color-ink);
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
}

.footer-content {
  max-width: 600px;
  margin: 0 auto;
}

.footer-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  flex-wrap: wrap;
  margin-bottom: var(--space-lg);
}

.footer-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  font-size: 14px;
  font-family: var(--font-display);
  transition: color 0.2s;
}

.footer-link:hover {
  color: var(--color-gold);
}

.link-icon {
  opacity: 0.7;
}

.footer-divider {
  color: rgba(255, 255, 255, 0.2);
}

.footer-copy {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
  font-family: var(--font-display);
  letter-spacing: 0.1em;
}
</style>
