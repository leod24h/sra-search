import 'element-plus/dist/index.css'
import './assets/css/tailwind.css'
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import Home from './views/Home.vue'
import Advanced from './views/Advanced.vue'
import Taxonomy from './views/Taxonomy.vue'
import View from './views/View.vue'
import Metadata from './views/Metadata.vue'
import Trial from './views/Trial.vue'
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community'; 

ModuleRegistry.registerModules([AllCommunityModule]);

const routes = [
  {
    path: '/view',
    name: 'View',
    component: View,
  },
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/trial',
    name: 'Trial',
    component: Trial,
  },
  {
    path: '/metadata/:accession',
    name: 'Metadata',
    component: Metadata,
  },
  {
    path: '/advanced',
    name: 'Advanced Search',
    component: Advanced
  },
  {
    path: '/taxonomy',
    name: 'Taxonomy',
    component: Taxonomy
  }
]
 
const router = createRouter({
  history: createWebHistory(),
  routes,
})

const pinia = createPinia();
 
const app = createApp(App)
app.use(router)
app.use(pinia)
app.mount('#app')

router.beforeEach((to, from, next) => {
  document.title = "SRA Metadata " + to.name;
  next();
});
