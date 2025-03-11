<template>
  <app-header/>
  <div class="max-w-6xl mx-auto py-8 px-12">

    <!-- Features Section -->
    <section>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- Curation Column -->
        <div class="text-gray-600">
          <h3 class="text-lg font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <svg-icon type="mdi" :path="mdiAutoFix_path" class="h-5 w-5 text-green-600" />
            Data Curation
          </h3>
          <p class="text-sm leading-relaxed">
            <b>SRA Metadata Search Engine</b> is enhanced by our meticulous curation process. We address gaps in data
            and extract key information.
            We enhance data completeness by curating missing geographical locations and collection dates.
            Additionally, latitude and longitude are extracted from attributes for accurate mapping.
          </p>
        </div>

        <!-- Search Column -->
        <div class="text-gray-600">
          <h3 class="text-lg font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-purple-500" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Better Search Experience
          </h3>
          <p class="text-sm leading-relaxed">
            The search functionality is powered by cutting-edge technology — <span class="text-blue-600 font-bold">semantic search</span> driven by LLMs, 
            embedding techniques and reranking algorithms to
            deliver highly relevant results.
            We also provide an advanced search feature for more granular control over search parameters.
          </p>
        </div>
      </div>
    </section>
    <!-- Statistics Section -->
    <section class="mt-12">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <!-- BioProjects Card -->
        <div class="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
          <div class="flex items-center gap-2 mb-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <h3 class="text-lg font-semibold text-gray-700">Complete BioProjects</h3>
          </div>
          <p class="text-2xl font-bold text-blue-600 text-center">583,982</p>
          <p class="text-gray-500 text-center mb-2">linked to its SRA Run</p>
          <p class="text-gray-400 text-[15px] text-right">Last updated on Feb, 2025</p>
        </div>

        <!-- SRA Runs Card -->
        <div class="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
          <div class="flex items-center gap-2 mb-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <h3 class="text-lg font-semibold text-gray-700">Complete SRA</h3>
          </div>
          <p class="text-2xl font-bold text-blue-600 text-center">35,200,294</p>
          <p class="text-gray-500 text-center mb-2">available for searching</p>
          <p class="text-gray-400 text-[15px] text-right">Last updated on Feb, 2025</p>
        </div>

        <!-- Taxonomy Tree Card -->
        <div class="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
          <div class="flex items-center gap-2 mb-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <h3 class="text-lg font-semibold text-gray-700">Curation of metadata</h3>
          </div>
          <p class="text-2xl font-bold text-blue-600 text-center">2,000,000</p>
          <p class="text-gray-400 text-center">applied curation</p>
        </div>
      </div>
    </section>
  </div>
  <div class="px-10">
    <div class="py-10">
      <p class="text-xl text-center mt-3 mb-3">SRA Distribution by Country</p>
      <map-selection></map-selection>
    </div>

  </div>
</template>

<script>
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiInformationVariantCircleOutline, mdiAutoFix } from '@mdi/js';
import MapSelection from '../components/MapSelection.vue';
import AppHeader from '../components/AppHeader.vue';

export default {
  components: {
    AppHeader,
    MapSelection,
    SvgIcon,
  },
  data() {
    return {
      inputValue: '',
      mdiInfo_path: mdiInformationVariantCircleOutline,
      mdiAutoFix_path: mdiAutoFix,
    };
  },
  methods: {
    
  }
};
</script>
