import { createRouter, createWebHistory } from 'vue-router';
import SurveyView from '../views/SurveyView.vue';
import ResultView from '../views/ResultView.vue';

const router = createRouter({
  history: createWebHistory('/app/'),
  routes: [
    {
      path: '/',
      redirect: { name: 'survey' }
    },
    {
      path: '/survey',
      name: 'survey',
      component: SurveyView
    },
    {
      path: '/result/:id',
      name: 'result',
      component: ResultView,
      props: true
    },
    {
      path: '/privacy',
      beforeEnter: () => {
        window.location.href = '/privacy.html';
      }
    },
    {
      path: '/terms',
      beforeEnter: () => {
        window.location.href = '/terms.html';
      }
    },
    {
      path: '/disclaimer',
      beforeEnter: () => {
        window.location.href = '/disclaimer.html';
      }
    },
    {
      path: '/legal/tokushoho',
      beforeEnter: () => {
        window.location.href = '/tokushoho.html';
      }
    },
    {
      path: '/landing',
      beforeEnter: () => {
        window.location.href = '/landing.html';
      }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: { name: 'survey' }
    }
  ]
});

export default router;
