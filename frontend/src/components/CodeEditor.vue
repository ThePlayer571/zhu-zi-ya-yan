<script setup lang="ts">
import { useProgramStore } from '../stores/program'

const store = useProgramStore()
</script>

<template>
  <div class="code-editor">
    <div class="editor-header">源码</div>
    <textarea
      v-model="store.sourceCode"
      :disabled="store.isRunning"
      placeholder="在此输入文言源码..."
      spellcheck="false"
      class="editor-textarea"
    />
  </div>
</template>

<style scoped>
.code-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-header {
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.editor-textarea {
  flex: 1;
  width: 100%;
  padding: 12px;
  border: none;
  outline: none;
  resize: none;
  font-family: 'Noto Sans SC', 'Source Han Sans SC', 'Microsoft YaHei', monospace;
  font-size: 16px;
  line-height: 1.8;
  color: #1f2937;
  background: #fff;
}

.editor-textarea:disabled {
  background: #f3f4f6;
  color: #9ca3af;
}

.editor-textarea::placeholder {
  color: #c4c4c4;
}
</style>
