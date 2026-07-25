<script setup lang="ts">
import { ref, onMounted } from 'vue'

const visible = ref(false)

onMounted(() => {
  visible.value = true
})

function scrollToEditor(): void {
  const el = document.getElementById('editor-section')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}

function scrollToChallenge(): void {
  const el = document.getElementById('challenge-section')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>

<template>
  <section class="hero">
    <!-- 背景装饰 -->
    <div class="hero-bg">
      <!-- 云纹 -->
      <div class="cloud cloud-1" />
      <div class="cloud cloud-2" />
      <div class="cloud cloud-3" />
      <div class="cloud cloud-4" />
      <!-- 远山 -->
      <svg class="mountains" viewBox="0 0 1440 200" preserveAspectRatio="none">
        <defs>
          <linearGradient id="inkWashFront" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#1a1410" stop-opacity="0.18" />
            <stop offset="40%" stop-color="#1a1410" stop-opacity="0.08" />
            <stop offset="100%" stop-color="#1a1410" stop-opacity="0.02" />
          </linearGradient>
          <linearGradient id="mistGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#f5f0e8" stop-opacity="0.5" />
            <stop offset="100%" stop-color="#f5f0e8" stop-opacity="0" />
          </linearGradient>
        </defs>
        <path
          d="M0,200 L0,95 Q100,75 220,90 Q340,105 460,80 Q560,58 680,78 Q800,100 920,72 Q1040,45 1160,85 Q1280,120 1440,70 L1440,200 Z"
          fill="#1a1410" fill-opacity="0.06"
        />
        <path
          d="M0,200 L0,120 Q140,90 280,110 Q420,130 540,95 Q660,60 780,100 Q900,140 1020,105 Q1140,70 1260,95 Q1380,120 1440,90 L1440,200 Z"
          fill="#1a1410" fill-opacity="0.12"
        />
        <path
          d="M0,200 L0,145 Q160,115 320,140 Q480,165 600,130 Q720,95 840,135 Q960,175 1080,140 Q1200,105 1320,130 Q1400,148 1440,125 L1440,200 Z"
          fill="url(#inkWashFront)"
        />
        <rect x="0" y="60" width="1440" height="90" fill="url(#mistGrad)" />
      </svg>
    </div>

    <!-- 顶部边框 -->
    <div class="top-border">
      <span class="top-border-corner top-border-left">╱</span>
      <span class="top-border-line" />
      <span class="top-border-diamond">◆</span>
      <span class="top-border-line" />
      <span class="top-border-corner top-border-right">╲</span>
    </div>

    <!-- 主内容 -->
    <div class="hero-content" :class="{ visible: visible }">
      <!-- Logo 区域 -->
      <div class="logo-area">
        <!-- 方形印章 -->
        <div class="seal-square">
          <svg class="seal-corner seal-corner-tl" viewBox="0 0 40 40">
            <path d="M0,16 Q0,0 16,0" stroke="currentColor" stroke-width="1.5" fill="none" />
            <path d="M0,16 L8,0" stroke="currentColor" stroke-width="1" fill="none" />
            <path d="M16,0 L0,8" stroke="currentColor" stroke-width="1" fill="none" />
          </svg>
          <svg class="seal-corner seal-corner-tr" viewBox="0 0 40 40">
            <path d="M40,16 Q40,0 24,0" stroke="currentColor" stroke-width="1.5" fill="none" />
            <path d="M40,16 L32,0" stroke="currentColor" stroke-width="1" fill="none" />
            <path d="M24,0 L40,8" stroke="currentColor" stroke-width="1" fill="none" />
          </svg>
          <div class="seal-cell">
            <span class="seal-char">诸</span>
          </div>
          <div class="seal-cell seal-cell-em">
            <span class="seal-char">子</span>
          </div>
          <div class="seal-cell">
            <span class="seal-char">雅</span>
          </div>
          <div class="seal-cell">
            <span class="seal-char">言</span>
          </div>
          <svg class="seal-corner seal-corner-bl" viewBox="0 0 40 40">
            <path d="M0,24 Q0,40 16,40" stroke="currentColor" stroke-width="1.5" fill="none" />
            <path d="M0,24 L8,40" stroke="currentColor" stroke-width="1" fill="none" />
            <path d="M16,40 L0,32" stroke="currentColor" stroke-width="1" fill="none" />
          </svg>
          <svg class="seal-corner seal-corner-br" viewBox="0 0 40 40">
            <path d="M40,24 Q40,40 24,40" stroke="currentColor" stroke-width="1.5" fill="none" />
            <path d="M40,24 L32,40" stroke="currentColor" stroke-width="1" fill="none" />
            <path d="M24,40 L40,32" stroke="currentColor" stroke-width="1" fill="none" />
          </svg>
        </div>

        <!-- 副标题 -->
        <div class="subtitle-block">
          <span class="subtitle-line" />
          <p class="subtitle-text">春秋时期编程语言</p>
          <span class="subtitle-line" />
        </div>
      </div>

      <!-- 设计哲学 -->
      <div class="philosophies">
        <div class="phil-item">
          <div class="phil-seal"><span class="phil-seal-char">壹</span></div>
          <p class="phil-text">
            <strong>句读</strong>，立章法之基。
          </p>
          <p class="phil-sub">以文言句读为语法骨架，使代码结构自然而严谨。</p>
        </div>
        <div class="phil-divider" />
        <div class="phil-item">
          <div class="phil-seal"><span class="phil-seal-char">贰</span></div>
          <p class="phil-text">
            <strong>尚文采</strong>，容万殊之变。
          </p>
          <p class="phil-sub">同一语义允许多种表达，如文言修辞般丰富多彩。</p>
        </div>
        <div class="phil-divider" />
        <div class="phil-item">
          <div class="phil-seal"><span class="phil-seal-char">叁</span></div>
          <p class="phil-text">
            <strong>撰码如属文</strong>，自然成章。
          </p>
          <p class="phil-sub">代码即文章，读之如诵古经，写之如作雅文。</p>
        </div>
      </div>

      <!-- 滚动按钮 -->
      <div class="scroll-area">
        <button class="scroll-btn" @click="scrollToEditor">
          <span class="scroll-btn-pill">
            <span class="scroll-label">试 之</span>
            <svg class="scroll-arrow" viewBox="0 0 24 24" width="18" height="18">
              <path d="M12 5v14M6 13l6 6 6-6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
        </button>
        <span class="challenge-hint" @click="scrollToChallenge">闯关试炼 ↓</span>
      </div>
    </div>

    <!-- 左右装饰 -->
    <div class="side-decor side-left">
      <span class="side-char">雅</span>
    </div>
    <div class="side-decor side-right">
      <span class="side-char">言</span>
    </div>
  </section>
</template>

<style scoped>
/* ===================================================================
   Section
   =================================================================== */

.hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background:
    repeating-linear-gradient(
      90deg,
      transparent 0px,
      transparent 2px,
      rgba(139, 115, 85, 0.015) 2px,
      rgba(139, 115, 85, 0.015) 3px
    ),
    repeating-linear-gradient(
      0deg,
      transparent 0px,
      transparent 3px,
      rgba(184, 134, 11, 0.008) 3px,
      rgba(184, 134, 11, 0.008) 4px
    ),
    linear-gradient(
      175deg,
      #faf7f0 0%,
      #f3ebd8 18%,
      #e9ddc5 40%,
      #e0d1b4 65%,
      #d7c5a5 85%,
      #d0bc99 100%
    );
  overflow: hidden;
}

.hero::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    ellipse 65% 55% at 50% 45%,
    transparent 25%,
    rgba(26, 20, 16, 0.06) 55%,
    rgba(26, 20, 16, 0.14) 85%,
    rgba(26, 20, 16, 0.20) 100%
  );
  pointer-events: none;
  z-index: 0;
}

/* ===================================================================
   Background Decor — Clouds (static)
   =================================================================== */

.hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.cloud {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(
    ellipse at center,
    rgba(220, 208, 186, 0.22) 0%,
    rgba(220, 208, 186, 0.10) 30%,
    transparent 70%
  );
}

.cloud::before {
  content: '';
  position: absolute;
  inset: -20px;
  border-radius: 50%;
  background: radial-gradient(
    ellipse at center,
    rgba(255, 248, 235, 0.12) 0%,
    transparent 60%
  );
}

.cloud-1 { top: 8%;  left: -5%;  width: 400px; height: 100px; }
.cloud-2 { top: 22%; right: -8%; width: 350px; height: 90px; }
.cloud-3 { bottom: 25%; left: 8%;  width: 280px; height: 70px; }
.cloud-4 { top: 55%; left: 30%;  width: 480px; height: 110px; }

/* ===================================================================
   Background Decor — Mountains
   =================================================================== */

.mountains {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 200px;
}

/* ===================================================================
   Top Border
   =================================================================== */

.top-border {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: var(--space-3xl);
  padding-top: var(--space-2xl);
}

.top-border-line {
  display: block;
  width: 100px;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--color-gold) 30%,
    var(--color-gold) 70%,
    transparent
  );
}

.top-border-diamond {
  font-size: 9px;
  color: var(--color-gold);
  opacity: 0.5;
}

.top-border-corner {
  font-size: 18px;
  color: var(--color-gold);
  opacity: 0.3;
  line-height: 1;
}

/* ===================================================================
   Hero Content
   =================================================================== */

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3xl);
  padding: var(--space-lg);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.hero-content.visible {
  opacity: 1;
}

/* ===================================================================
   Logo Area
   =================================================================== */

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xl);
}

/* ---- Square Seal ---- */

.seal-square {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 12px;
  padding: var(--space-2xl);
  border: 1px solid rgba(184, 134, 11, 0.2);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.3);
  box-shadow:
    0 4px 30px rgba(26, 20, 16, 0.05),
    inset 0 0 50px rgba(184, 134, 11, 0.02);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.seal-square:hover {
  transform: translateY(-2px);
  box-shadow:
    0 8px 36px rgba(26, 20, 16, 0.08),
    inset 0 0 50px rgba(184, 134, 11, 0.03);
}

.seal-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  aspect-ratio: 1;
}

.seal-char {
  font-family: var(--font-display);
  font-size: 84px;
  font-weight: 900;
  color: var(--color-ink);
  line-height: 1;
  transition: color 0.25s ease;
  cursor: default;
  user-select: none;
}

.seal-char:hover {
  color: var(--color-vermillion);
}

.seal-cell-em .seal-char {
  color: var(--color-ink);
}

/* Seal corner ornaments */
.seal-corner {
  position: absolute;
  width: 32px;
  height: 32px;
  color: var(--color-gold);
  opacity: 0.35;
}

.seal-corner-tl { top: 8px; left: 8px; }
.seal-corner-tr { top: 8px; right: 8px; }
.seal-corner-bl { bottom: 8px; left: 8px; }
.seal-corner-br { bottom: 8px; right: 8px; }

/* ===================================================================
   Subtitle
   =================================================================== */

.subtitle-block {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.subtitle-text {
  font-family: var(--font-display);
  font-size: 17px;
  color: var(--color-ink-light);
  letter-spacing: 0.3em;
  white-space: nowrap;
}

.subtitle-line {
  display: block;
  width: 50px;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(184, 134, 11, 0.35) 30%,
    rgba(184, 134, 11, 0.35) 70%,
    transparent
  );
}

/* ===================================================================
   Philosophies — 简牍卡片
   =================================================================== */

.philosophies {
  display: flex;
  align-items: stretch;
  gap: 0;
  max-width: 820px;
}

.phil-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  position: relative;
  padding: var(--space-lg) var(--space-md) var(--space-lg) 28px;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.45) 0%,
    rgba(245, 240, 228, 0.25) 100%
  );
  border-left: 3px solid rgba(196, 30, 58, 0.4);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  box-shadow:
    0 2px 12px rgba(26, 20, 16, 0.04),
    inset 0 0 20px rgba(184, 134, 11, 0.015);
  min-height: 150px;
  transition: transform 0.3s ease,
              border-left-color 0.3s ease,
              box-shadow 0.3s ease;
}

.phil-item::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 12px;
  right: 12px;
  height: 1.5px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(184, 134, 11, 0.25) 20%,
    rgba(184, 134, 11, 0.25) 80%,
    transparent
  );
  border-radius: 1px;
}

.phil-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(26, 20, 16, 0.06);
  border-left-color: rgba(196, 30, 58, 0.65);
}

/* ---- Philosophy Seal Stamp ---- */

.phil-seal {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1.5px solid rgba(196, 30, 58, 0.45);
  border-radius: 3px;
  background: rgba(196, 30, 58, 0.05);
  transform: rotate(3deg);
}

.phil-seal-char {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 800;
  color: var(--color-vermillion);
  line-height: 1;
}

/* ---- Philosophy Text ---- */

.phil-text {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--color-ink-light);
  line-height: 1.7;
  letter-spacing: 0.04em;
  margin-bottom: var(--space-xs);
  padding-right: 40px;
}

.phil-text strong {
  color: var(--color-ink);
  font-weight: 800;
}

.phil-sub {
  font-size: 13px;
  color: var(--color-slate);
  line-height: 1.7;
  opacity: 0.82;
}

/* ---- Philosophy Divider ---- */

.phil-divider {
  width: 1px;
  background: linear-gradient(
    180deg,
    transparent,
    rgba(184, 134, 11, 0.22) 25%,
    rgba(184, 134, 11, 0.22) 75%,
    transparent
  );
  align-self: stretch;
  margin: var(--space-lg) var(--space-sm);
  flex-shrink: 0;
}

/* ===================================================================
   Scroll CTA Button
   =================================================================== */

.scroll-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: transparent;
  border: none;
  cursor: pointer;
  font-family: var(--font-display);
}

.scroll-btn-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 40px;
  background: var(--color-vermillion);
  border: 2px solid rgba(184, 134, 11, 0.55);
  border-radius: 30px;
  box-shadow:
    0 0 0 4px rgba(196, 30, 58, 0.12),
    0 4px 20px rgba(196, 30, 58, 0.2);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
}

.scroll-btn-pill::before {
  content: '';
  position: absolute;
  inset: 3px;
  border: 1px solid rgba(184, 134, 11, 0.18);
  border-radius: 26px;
  pointer-events: none;
}

.scroll-btn:hover .scroll-btn-pill {
  transform: translateY(-2px);
  background: var(--color-vermillion-dark);
  border-color: rgba(212, 167, 69, 0.75);
  box-shadow:
    0 0 0 4px rgba(196, 30, 58, 0.16),
    0 8px 30px rgba(196, 30, 58, 0.32);
}

.scroll-btn:active .scroll-btn-pill {
  transform: translateY(0);
}

.scroll-label {
  font-size: 19px;
  font-weight: 800;
  color: #fff;
  letter-spacing: 0.6em;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.12);
}

.scroll-arrow {
  color: rgba(255, 255, 255, 0.65);
  flex-shrink: 0;
}

/* ---- Scroll Area Wrapper ---- */

.scroll-area {
  position: relative;
  display: inline-flex;
}

/* ---- Challenge Hint ---- */

.challenge-hint {
  position: absolute;
  left: calc(100% + 14px);
  top: 50%;
  transform: translateY(-50%);
  font-family: var(--font-display);
  font-size: 13px;
  color: var(--color-vermillion);
  letter-spacing: 0.1em;
  cursor: pointer;
  transition: color 0.2s;
  user-select: none;
  white-space: nowrap;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.challenge-hint:hover {
  color: var(--color-vermillion-dark);
}

/* ===================================================================
   Side Decorations
   =================================================================== */

.side-decor {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  z-index: 0;
}

.side-decor.side-left  { left: 5%; }
.side-decor.side-right { right: 5%; }

.side-char {
  display: block;
  font-family: var(--font-display);
  font-size: 150px;
  font-weight: 900;
  color: rgba(184, 134, 11, 0.08);
  line-height: 1;
  user-select: none;
  transform: rotate(-3deg);
}

.side-right .side-char {
  transform: rotate(3deg);
}

/* ===================================================================
   Responsive — Large screens
   =================================================================== */

@media (min-width: 1400px) {
  .seal-char {
    font-size: 96px;
  }

  .philosophies {
    max-width: 900px;
  }
}

/* ===================================================================
   Responsive — Tablet
   =================================================================== */

@media (max-width: 1024px) {
  .side-decor {
    display: none;
  }
}

/* ===================================================================
   Responsive — Mobile
   =================================================================== */

@media (max-width: 768px) {
  .seal-square {
    padding: var(--space-lg) var(--space-xl);
  }

  .seal-char {
    font-size: 56px;
  }

  .seal-corner {
    width: 24px;
    height: 24px;
  }

  .subtitle-text {
    font-size: 14px;
    letter-spacing: 0.2em;
  }

  .subtitle-line {
    width: 30px;
  }

  .philosophies {
    flex-direction: column;
    gap: 0;
    align-items: stretch;
    max-width: 340px;
  }

  .phil-item {
    min-height: auto;
  }

  .phil-divider {
    width: auto;
    height: 1px;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(184, 134, 11, 0.22) 25%,
      rgba(184, 134, 11, 0.22) 75%,
      transparent
    );
    margin: var(--space-sm) var(--space-lg);
  }

  .scroll-btn-pill {
    padding: 12px 32px;
  }

  .scroll-label {
    font-size: 16px;
  }

  .hero-content {
    gap: var(--space-2xl);
  }
}
</style>
