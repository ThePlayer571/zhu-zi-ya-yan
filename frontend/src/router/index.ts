import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import ChallengeSelect from '../views/ChallengeSelect.vue'
import ChallengeLevel from '../views/ChallengeLevel.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
    },
    {
      path: '/challenge',
      name: 'challenge-select',
      component: ChallengeSelect,
    },
    {
      path: '/challenge/:id',
      name: 'challenge-level',
      component: ChallengeLevel,
      props: true,
    },
  ],
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
})

export default router
