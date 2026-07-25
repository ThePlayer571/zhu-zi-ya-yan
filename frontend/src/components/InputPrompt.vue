<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useProgramStore } from '../stores/program'

const store = useProgramStore()
const inputText = ref('')
const inputEl = ref<HTMLInputElement | null>(null)

/** 当进入等待输入状态时自动聚焦输入框。 */
watch(
  () => store.isAwaitingInput,
  async (val) => {
    if (val) {
      inputText.value = ''
      await nextTick()
      inputEl.value?.focus()
    }
  },
)

function submit(): void {
  const text = inputText.value.trim()
  if (!text) return
  store.provideInput(text)
}
</script>

<template>
  <div v-if="store.isAwaitingInput" class="input-prompt">
    <div class="input-header">输入</div>
    <div class="input-body">
      <label v-if="store.inputPrompt" class="input-label">
        {{ store.inputPrompt }}
      </label>
      <div class="input-row">
        <input
          ref="inputEl"
          v-model="inputText"
          type="text"
          class="input-field"
          placeholder="在此输入..."
          @keyup.enter="submit"
        />
        <button class="input-submit" @click="submit">输入</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.input-prompt {
  border-top: 2px solid #f59e0b;
  flex-shrink: 0;
}

.input-header {
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 600;
  color: #d97706;
  background: #fffbeb;
  border-bottom: 1px solid #fde68a;
}

.input-body {
  padding: 10px 12px;
  background: #fffbeb;
}

.input-label {
  display: block;
  font-size: 14px;
  color: #92400e;
  margin-bottom: 6px;
}

.input-row {
  display: flex;
  gap: 8px;
}

.input-field {
  flex: 1;
  padding: 6px 10px;
  font-size: 15px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  outline: none;
}

.input-field:focus {
  border-color: #f59e0b;
  box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.15);
}

.input-submit {
  padding: 6px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  background: #d97706;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.input-submit:hover {
  background: #b45309;
}
</style>
