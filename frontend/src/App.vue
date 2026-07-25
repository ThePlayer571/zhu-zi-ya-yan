<script setup lang="ts">
import { onMounted } from 'vue'
import { useProgramStore } from './stores/program'
import CodeEditor from './components/CodeEditor.vue'
import RunButton from './components/RunButton.vue'
import OutputDisplay from './components/OutputDisplay.vue'
import InputPrompt from './components/InputPrompt.vue'
import TracePanel from './components/TracePanel.vue'

const store = useProgramStore()

onMounted(() => {
  store.connect()
})
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <h1 class="app-title">诸子雅言</h1>
      <span class="app-subtitle">春秋时期古文风编程语言</span>
    </header>
    <RunButton />
    <div class="main-panels">
      <CodeEditor class="panel-left" />
      <div class="panel-right">
        <OutputDisplay />
        <InputPrompt />
        <TracePanel />
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
  border-left: 1px solid #e5e7eb;
  border-right: 1px solid #e5e7eb;
}

.app-header {
  padding: 12px 16px;
  background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
  color: #fff;
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-shrink: 0;
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  font-family: 'Noto Serif SC', 'Source Han Serif SC', 'SimSun', serif;
}

.app-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.main-panels {
  flex: 1;
  display: flex;
  min-height: 0;
}

.panel-left {
  width: 50%;
  border-right: 1px solid #e5e7eb;
}

.panel-right {
  width: 50%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
</style>
