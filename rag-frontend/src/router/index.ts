import { createRouter, createWebHistory } from 'vue-router'
import DocManage from '../views/DocManage.vue'
import RagQuery from '../views/RagQuery.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'doc-manage',
      component: DocManage
    },
    {
      path: '/query',
      name: 'rag-query',
      component: RagQuery
    }
  ]
})

export default router
