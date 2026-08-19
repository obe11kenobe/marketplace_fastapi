<script setup>
defineProps({
  value: { type: Number, default: 0 },
  editable: { type: Boolean, default: false },
})

const emit = defineEmits(['update:value'])
</script>

<template>
  <div class="stars" :class="{ editable }" :role="editable ? 'radiogroup' : 'img'"
       :aria-label="editable ? 'Оценка' : `Оценка ${value} из 5`">
    <component :is="editable ? 'button' : 'span'"
               v-for="n in 5" :key="n"
               :type="editable ? 'button' : undefined"
               :aria-label="editable ? `${n} из 5` : undefined"
               :aria-checked="editable ? value === n : undefined"
               :role="editable ? 'radio' : undefined"
               class="star" :class="{ on: n <= value }"
               @click="editable && emit('update:value', n)">
      <svg width="17" height="17" viewBox="0 0 24 24" :fill="n <= value ? 'currentColor' : 'none'"
           stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true">
        <path d="M12 2.6l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5-5.8-3-5.8 3 1.1-6.5L2.6 9.4l6.5-.9z" />
      </svg>
    </component>
  </div>
</template>

<style scoped>
.stars {
  display: inline-flex;
  gap: 2px;
  color: var(--border-strong);
}

.star {
  display: grid;
  place-items: center;
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  line-height: 0;
}

.star.on {
  color: var(--warning);
}

.editable .star {
  cursor: pointer;
  padding: 2px;
  transition: transform 0.12s ease;
}

.editable .star:hover {
  transform: scale(1.15);
}
</style>
