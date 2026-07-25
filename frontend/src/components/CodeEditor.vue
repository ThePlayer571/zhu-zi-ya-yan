<script setup lang="ts">
defineProps<{
  modelValue: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

function onInput(event: Event): void {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="code-editor">
    <div class="editor-header">
      <span class="header-icon">◈</span>
      <span>源码</span>
    </div>
    <textarea
      :value="modelValue"
      :disabled="disabled"
      placeholder="在此输入文言源码…"
      spellcheck="false"
      class="editor-textarea"
      @input="onInput"
    />
  </div>
</template>

<style scoped>
.code-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
}

.editor-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-slate);
  background: #fafaf8;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
  font-family: var(--font-display);
}

.header-icon {
  color: var(--color-gold);
  font-size: 10px;
}

.editor-textarea {
  flex: 1;
  width: 100%;
  padding: 16px;
  border: none;
  outline: none;
  resize: none;
  font-family: var(--font-code);
  font-size: 17px;
  line-height: 2;
  color: var(--color-ink);
  background: #fff;
}

.editor-textarea:disabled {
  background: #fafaf8;
  color: var(--color-slate-light);
}

.editor-textarea::placeholder {
  color: #c4c0b8;
  font-style: italic;
}
</style>
