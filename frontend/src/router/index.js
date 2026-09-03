import { createRouter, createWebHashHistory } from 'vue-router'
import ReadingRoomView from '@/views/ReadingRoomView.vue'
import ArchivesView from '@/views/ArchivesView.vue'
import SettingsView from '@/views/SettingsView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'reading-room', component: ReadingRoomView },
    { path: '/archives', name: 'archives', component: ArchivesView },
    { path: '/settings', name: 'settings', component: SettingsView },
  ],
})

export default router