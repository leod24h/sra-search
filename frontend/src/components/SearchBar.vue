<!-- 
There is history dropdown in the search bar, but it is disabled in the current version.
-->
<template>
  <div class="z-auto">
    <!-- Search Container -->
    <div class="relative" @click.stop>
      <!-- Search Input and History Container -->
      <div class="border border-gray-300 transition-all duration-300 bg-white shadow-md"
        :class="{ 'rounded-t-3xl': showHistory && searchHistory.length > 0, 'rounded-3xl': !showHistory || searchHistory.length === 0 }">
        <!-- Search Input -->
        <div class="flex items-center">
          <span class="pl-3 pr-2 text-gray-400">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </span>
          <input :value="modelValue" type="text" placeholder=""
            class="w-full py-2 px-1 mr-5 focus:outline-none" 
            @input="$emit('update:modelValue', $event.target.value)"
            @keypress.enter="handleSearch" />
            <!-- @focus="showHistory = true" -->

        </div>

        <!-- Search History (expanded below input, separated by divider) -->
        <!-- <div v-if="showHistory && searchHistory.length > 0" ref="historyDropdown"
          class="absolute inset-x-0 bg-white border-gray-300 rounded-b-3xl border-b border-x shadow-md">
          <div class="border-t border-gray-300 mx-auto "></div>
          <div class="my-1">
            <ul class="max-h-48 overflow-y-auto text-left">
              <li v-for="(item, index) in searchHistory" :key="index" class="px-5 hover:bg-gray-100 cursor-pointer rounded-md"
                @click="selectHistoryItem(item)">
                {{ item }}
              </li>
            </ul>
          </div> -->
          <!-- Search buttom -->
          <!-- <div class="flex mb-2 text-sm">
            <button class="mx-auto px-4 py-1 text-center border-2 border-gray-50 rounded-sm text-gray-700 bg-gray-50 hover:border-blue-300">
              Search
            </button>
          </div> -->
        <!-- </div> -->
      </div>
    </div>
  </div>
</template>

<script>
import { useSearchStore } from "../stores/store.js";
import { toRefs } from "vue";

export default {
  name: 'SearchBar',
  setup() {
    const searchStore = useSearchStore();
    const state = toRefs(searchStore);
    return {
      ...state,
      addSearchHistory: searchStore.addSearchHistory
    };
  },
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      // modelValue: '',
      showHistory: false,
    }
  },
  mounted() {
    document.addEventListener("click", this.handleClickOutside);
  },
  unmounted() {
    document.removeEventListener("click", this.handleClickOutside);
  },
  methods: {
    handleSearch() {
      if (this.modelValue.trim()) {
        this.addSearchHistory(this.modelValue.trim());
        this.$emit('search'); // Emit a custom event for the search action
      }
    },
    selectHistoryItem(item) {
      this.modelValue = item
      this.showHistory = false
      this.handleSearch();
    },
    hideHistory() {
      this.showHistory = false
    },
    handleClickOutside(event) {
      this.showHistory = false;
    },
  }
}
</script>