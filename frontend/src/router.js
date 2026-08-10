import { createRouter, createWebHistory } from 'vue-router'
import CatalogView from './views/CatalogView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'catalog', component: CatalogView },
    {
      path: '/category/:id',
      name: 'category',
      component: CatalogView,
      props: (route) => ({ categoryId: Number(route.params.id) }),
    },
    {
      path: '/product/:id',
      name: 'product',
      component: () => import('./views/ProductView.vue'),
      props: (route) => ({ id: Number(route.params.id) }),
    },
    { path: '/cart', name: 'cart', component: () => import('./views/CartView.vue') },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('./views/NotFoundView.vue') },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
