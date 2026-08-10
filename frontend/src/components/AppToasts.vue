<script setup>
import { toasts } from '../toast'
</script>

<template>
  <div class="stack" role="status" aria-live="polite">
    <TransitionGroup name="fade">
      <div v-for="t in toasts.items" :key="t.id" class="toast card" :class="t.type">
        {{ t.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.stack {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.toast {
  padding: 12px 16px;
  box-shadow: var(--shadow-lg);
  font-size: 14px;
  font-weight: 500;
  border-left: 3px solid var(--success);
  max-width: 320px;
}

.toast.error {
  border-left-color: var(--danger);
  color: var(--danger);
}

@media (max-width: 560px) {
  .stack {
    left: 16px;
    right: 16px;
  }
}
</style>
