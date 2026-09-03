<template>
  <div class="app-layout">
    <Sidebar />
    <main class="main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from '@/store'
import Sidebar from '@/components/Sidebar.vue'

const store = useAppStore()

onMounted(() => {
  store.loadDatasets().catch(() => {})
})
</script>