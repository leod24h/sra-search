import 'element-plus/dist/index.css'
import './assets/css/tailwind.css'
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import Home from '@/views/Home.vue'
import BioStudy from '@/views/BioStudy.vue'
import Sample from '@/views/Sample.vue'
import Taxonomy from '@/views/Taxonomy.vue'
import SampleResult from '@/views/SampleResult.vue'
import StudyResult from '@/views/StudyResult.vue'
import Metadata from '@/views/Metadata.vue'
import Trial from '@/views/Trial.vue'
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community'; 

ModuleRegistry.registerModules([AllCommunityModule]);

const routes = [
  {
    path: '/sample_result',
    name: 'Sample Result',
    component: SampleResult,
  },
  {
    path: '/study_result',
    name: 'Study Result',
    component: StudyResult,
  },
  {
    path: '/',
    name: 'Home',
    component: Home,
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
    path: '/study',
    name: 'Study Search',
    component: BioStudy,
  },
  {
    path: '/sample',
    name: 'Sample Search',
    component: Sample,
  },
  {
    path: '/taxonomy',
    name: 'Taxonomy',
    component: Taxonomy,
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
