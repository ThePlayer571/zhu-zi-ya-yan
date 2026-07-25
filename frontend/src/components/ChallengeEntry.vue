<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goToChallenge(): void {
  router.push('/challenge')
}
</script>

<template>
  <section id="challenge-section" class="challenge-entry">
    <div class="entry-content">
      <h2 class="entry-title">闯关试炼</h2>
      <p class="entry-desc">
        以文言编程，解题攻关。如临春秋之试，展君子之才。
      </p>
      <button class="entry-btn" @click="goToChallenge">
        <span>入关</span>
        <svg viewBox="0 0 24 24" width="16" height="16" class="entry-arrow">
          <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </button>
    </div>
  </section>
</template>

<style scoped>
.challenge-entry {
  min-height: 40vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-2xl);
  background: linear-gradient(180deg, #ede6d8 0%, #e0d6c4 100%);
  text-align: center;
}

.entry-content {
  max-width: 480px;
}

.entry-title {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 900;
  color: var(--color-ink);
  margin-bottom: var(--space-md);
  letter-spacing: 0.15em;
}

.entry-desc {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--color-slate);
  line-height: 1.8;
  margin-bottom: var(--space-xl);
}

.entry-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 40px;
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.2em;
  color: #fff;
  background: var(--color-vermillion);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.entry-btn:hover {
  background: var(--color-vermillion-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(196, 30, 58, 0.25);
}

.entry-arrow {
  transition: transform 0.2s;
}

.entry-btn:hover .entry-arrow {
  transform: translateX(3px);
}
</style>
