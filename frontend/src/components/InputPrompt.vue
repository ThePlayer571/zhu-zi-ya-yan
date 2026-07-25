<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

const props = withDefaults(defineProps<{
  visible: boolean
  promptText: string | null
  allowEmpty?: boolean
}>(), {
  allowEmpty: false,
})

const emit = defineEmits<{
  submit: [text: string]
}>()

const inputText = ref('')
const inputEl = ref<HTMLInputElement | null>(null)

watch(
  () => props.visible,
  async (val) => {
    if (val) {
      inputText.value = ''
      await nextTick()
      inputEl.value?.focus()
    }
  },
)

function handleSubmit(): void {
  const text = inputText.value.trim()
  if (!text && !props.allowEmpty) return
  emit('submit', props.allowEmpty ? inputText.value : text)
}
</script>

<template>
  <div v-if="visible" class="input-prompt">
    <div class="input-header">
      <span class="header-icon">◆</span>
      <span>输入</span>
    </div>
    <div class="input-body">
      <label v-if="promptText" class="input-label">
        {{ promptText }}
      </label>
      <div class="input-row">
        <input
          ref="inputEl"
          v-model="inputText"
          type="text"
          class="input-field"
          placeholder="在此输入…"
          @keyup.enter="handleSubmit"
        />
        <button class="input-submit" @click="handleSubmit">呈上</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.input-prompt {
  border-top: 2px solid var(--color-gold);
  flex-shrink: 0;
}

.input-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-gold);
  background: #fdfcf7;
  border-bottom: 1px solid var(--color-border-light);
  font-family: var(--font-display);
}

.header-icon {
  font-size: 10px;
}

.input-body {
  padding: 12px 16px;
  background: #fdfcf7;
}

.input-label {
  display: block;
  font-size: 14px;
  color: var(--color-ink-light);
  margin-bottom: 8px;
  font-family: var(--font-display);
}

.input-row {
  display: flex;
  gap: 8px;
}

.input-field {
  flex: 1;
  padding: 8px 12px;
  font-size: 16px;
  font-family: var(--font-code);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  outline: none;
  background: #fff;
  color: var(--color-ink);
}

.input-field:focus {
  border-color: var(--color-gold);
  box-shadow: 0 0 0 2px rgba(184, 134, 11, 0.12);
}

.input-submit {
  padding: 8px 18px;
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-display);
  color: #fff;
  background: var(--color-gold);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.2s;
}

.input-submit:hover {
  background: var(--color-gold-light);
}
</style>
