<template>
  <div class="w-full mx-auto py-12 mb-10 px-12">
    <h2 class="text-2xl font-bold mb-4">Advanced Search</h2>
    <p class="text-gray-600 text-sm mb-1">
      Unlock powerful search capabilities to refine your results and find exactly what you need. Use keywords, filters,
      and advanced operators to narrow down your search efficiently.
    </p>
    <p class="text-blue-600 text-sm mb-4"></p>
    <div class="flex flex-col">
      <search-bar v-model="inputValue" @search="handleSearch"></search-bar>
      
    </div>
    <div class="mt-5">
      <h3 class="text-base font-semibold mb-2">Filters</h3>
    </div>
    <div class="space-y-4">
      <!-- Filter Rows -->
      <div v-for="(filter, index) in filters" :key="index" class="flex items-start space-x-2">
        <!-- Logical Operator -->
        <select v-if="index > 0" v-model="filter.operator"
          class="border border-gray-300 rounded-md px-2 py-1 text-sm focus:ring-blue-500 focus:border-blue-500">
          <option value="AND">AND</option>
          <option value="OR">OR</option>
          <option value="NOT">NOT</option>
        </select>

        <!-- Field Dropdown -->
        <select v-model="filter.field"
          class="border border-gray-300 rounded-md px-2 py-1 text-sm focus:ring-blue-500 focus:border-blue-500">
          <option v-for="key in filterKeys" :key="key.value" :value="key.value">
            {{ key.label }}
          </option>
        </select>

        <!-- Value Input -->
        <div class="flex-1 z-10">
          <div v-if="filter.field === 'acc'">
            <el-input v-model="filter.value" placeholder="eg. SRR123456, SRR234567" clearable />
          </div>
          <div v-if="filter.field === 'organism'">
            <organism-select-autocomplete v-model="filter.value" />
            <input type="checkbox" v-model="filter.additional" />
            <span class="pl-2 text-[15px]">include its children in taxonomy</span>
          </div>
          <div v-if="filter.field === 'date'">
            <el-date-picker v-model="filter.value" type="monthrange" unlink-panels range-separator="To"
              start-placeholder="Start month" end-placeholder="End month" />
          </div>
          <div v-if="filter.field === 'geo'">
            <el-input v-model="filter.value" placeholder="e.g. Hong Kong" clearable />
          </div>
          <div v-if="filter.field === 'attribute'">
            <el-input v-model="filter.value" placeholder="e.g. tissue: blood" clearable />
          </div>

        </div>

        <!-- Remove Filter Button -->
        <button @click="removeFilter(index)" class="text-red-500 hover:text-red-700">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
            stroke="currentColor" class="w-5 h-5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Add Filter Button -->
      <button @click="addFilter" class="flex items-center text-blue-500 hover:text-blue-700">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"
          class="w-5 h-5 mr-1">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        Add Filter
      </button>

      <!-- Search button -->
      <div class="flex mt-4 mb-2 text-sm">
        <button @click="handleSearch"
          class="mx-auto px-4 py-1 text-center border-2 border-gray-50 rounded-sm text-gray-700 bg-gray-50 hover:border-blue-300">
          Search
        </button>
      </div>
    </div>


  </div>
</template>

<script>
import {
  ElCollapse, ElCollapseItem, ElForm, ElFormItem, ElPopover, ElInput, ElAutocomplete, ElDatePicker, ElButton,
  ElCol, ElRow, ElTable, ElTableColumn, ElTag, ElSelect, ElOption, ElSwitch
} from 'element-plus';
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiInformationVariantCircleOutline, mdiFilterOutline, mdiPlus, mdiClose, mdiChevronDown } from '@mdi/js';
import { useSearchStore } from '../stores/store.js';
import { toRefs } from 'vue';
import OrganismWikiTooltip from './OrganismWikiTooltip.vue';
import OrganismSelectAutocomplete from './OrganismSelectAutocomplete.vue';
import DescSelectAutocomplete from './DescSelectAutocomplete.vue';
import SearchBar from './SearchBar.vue';

export default {
  setup() {
    const searchStore = useSearchStore();
    const state = toRefs(searchStore);
    return {
      ...state,
      switchAdvancedSearchDialogVisible: searchStore.switchAdvancedSearchDialogVisible,
    };
  },
  components: {
    SvgIcon,
    ElCollapse,
    ElCollapseItem,
    ElForm,
    ElFormItem,
    ElPopover,
    ElInput,
    ElAutocomplete,
    ElDatePicker,
    ElButton,
    ElRow,
    ElCol,
    ElTable,
    ElTableColumn,
    ElTag,
    ElSelect,
    ElOption,
    ElSwitch,
    OrganismWikiTooltip,
    OrganismSelectAutocomplete,
    DescSelectAutocomplete,
    SearchBar,
  },
  data() {
    return {
      filters: [
        { operator: "AND", field: "acc", value: "", additional: "" },
      ],
      filterKeys: [
        { value: "acc", label: "Accession" },
        { value: "organism", label: "Organism" },
        { value: "date", label: "Date" },
        { value: "geo", label: "Geographical Location" },
        { value: "attribute", label: "Attributes" },
      ],
      inputValue: "", 
    };
  },
  methods: {
    addFilter() {
      this.filters.push({ operator: "AND", field: "acc", value: "" });
    },
    removeFilter(index) {
      this.filters.splice(index, 1);
    },
    constructFilters() {
      return this.filters
        .filter((filter) => filter.value) // Only include filters with a non-empty value
        .map((filter) => ({
          operator: filter.operator,
          field: filter.field,
          value: filter.value,
          additional: filter.additional ? filter.additional.toString() : "",
        }));
    },
    handleSearch() {
      this.input_query = this.inputValue.trim();
      this.input_filters = this.constructFilters();
      this.input_filters = JSON.stringify(this.input_filters);
      console.log(this.input_query, this.input_filters);
      this.$router.push({
        path: '/view',
        query: { search: this.input_query, filters: this.input_filters },
      });
    },
  },
};
</script>