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
      path: '/:pathMatch(.*)*',
      redirect: { name: 'survey' }
    }
  ]
});

export default router;
