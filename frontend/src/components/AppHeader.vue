<template>
  <header class="relative bg-cover bg-center h-[500px] flex items-center justify-center"
    style="background-image: url(' science-background.jpeg');">
    <!-- Gradient Overlay -->
    <div class="absolute inset-0 bg-gradient-to-r from-blue-800 to-blue-800 opacity-70"></div>

    <!-- Content -->
    <div class="relative z-10 text-center">
      <h1 class="text-4xl font-extrabold text-white mb-4">
        Unlock Insights with <span class="">SRA Metadata Search</span>
      </h1>
      <p class="text-lg text-gray-200 mb-6 max-w-xl mx-auto">
        Search and filter millions of data through AI.
      </p>

      <!-- Search Bar -->
      <!-- <div class="mt-6">
      <search-bar v-model="inputValue" @search="handleSearch"></search-bar>
      <div class="flex mt-4 mb-2 text-sm">
        <button
          @click="handleSearch"
          class="mx-auto px-4 py-1 text-center border-2 border-gray-50 rounded-sm text-gray-700 bg-gray-50 hover:border-blue-300">
          Search
        </button>
      </div>
    </div> -->
      <!-- Buttons -->
      <!-- Buttons -->
      <div class="flex justify-center space-x-4">
        <button
          @click="$router.push('/study')"
          class="flex items-center px-6 py-3 rounded bg-indigo-50 text-slate-600 font-semibold shadow-md hover:bg-indigo-200 transition-all">
          Search by Study
        </button>
        <button
          class="flex items-center px-6 py-3 rounded bg-indigo-50 text-slate-600 font-semibold shadow-md hover:bg-indigo-200 transition-all">
          
          Search by Sample
        </button>
      </div>
    </div>
  </header>
</template>

<script>
import MainMenu from "./MainMenu.vue";
import SearchBar from "./SearchBar.vue";
import SvgIcon from "@jamescoyle/vue-icon";
import { mdiMagnify, mdiChartTimelineVariantShimmer } from "@mdi/js";
import { useSearchStore } from "../stores/store.js";
import { toRefs } from "vue";

export default {
  setup() {
    const searchStore = useSearchStore();
    const state = toRefs(searchStore);
    return {
      ...state,
    };
  },
  components: {
    SearchBar,
    SvgIcon,
    MainMenu,
  },
  data() {
    return {
      inputValue: "",
      mdiMagnify_path: mdiMagnify,
    };
  },
  methods: {
    handleSearch() {
      if (this.inputValue.trim()) {
        this.$router.push({
          path: '/view',
          query: { search: this.inputValue.trim() },
        });
        this.input_query = this.inputValue.trim();
      }
    },

  },
};
</script>