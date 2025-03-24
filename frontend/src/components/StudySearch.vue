<template>
    <div class="w-full mx-auto py-12 mb-10 px-12">
        <h2 class="text-2xl font-bold mb-4">Search by study</h2>
        <p class="text-gray-600 text-sm mb-1">
            <!-- Unlock powerful search capabilities to refine your results and find exactly what you need. Use keywords, filters,
        and advanced operators to narrow down your search efficiently. -->
        </p>
        <p class="text-blue-600 text-sm mb-4"></p>
        <div class="flex flex-col">
            <search-bar v-model="inputValue" @search="handleSearch"></search-bar>
        </div>

        <!-- Examples -->
        <div class="mt-4 mb-4 text-gray-500 text-xs flex items-center">
            <div class=" flex flex-row space-x-2 ">
                <div class="rounded px-2 py-1 cursor-pointer text-gray-800 bg-gray-50" @click="setExample('Malaysian forest animal')">
                    Malaysian forest animal
                </div>
                <div class="rounded px-2 py-1 cursor-pointer text-gray-800 bg-gray-50" @click="setExample('ESBL')">
                    ESBL
                </div>
            </div>
        </div>

        <!-- Radio button -->
        <h2 class="text-md font-semibold text-gray-600">Search mode</h2>
        <div class="text-xs w-fit">
            <div class="flex flex-col px-2 py-3">
                <label class="flex items-center cursor-pointer">
                    <input type="radio" value="full" v-model="searchMode" class="hidden peer" />
                    <div
                        class="px-3 py-1 rounded border bg-gray-100 text-gray-600 font-medium transition-all peer-checked:text-blue-500 peer-checked:bg-blue-100 text-center flex-1">
                        Full-text search
                    </div>
                </label>

                <label class="flex items-center cursor-pointer mt-2">
                    <input type="radio" value="semantic" v-model="searchMode" class="hidden peer" />
                    <div
                        class="px-3 py-1 rounded border bg-gray-100 text-gray-600 font-medium transition-all peer-checked:text-violet-500 peer-checked:bg-violet-100 text-center flex-1">
                        Semantic search
                    </div>
                </label>
            </div>
        </div>

        <!-- Search button -->
        <div class="flex mt-4 mb-2 text-sm">
            <button @click="handleSearch"
                class="mx-auto w-fit px-4 py-1 text-center border-2 border-gray-50 rounded-sm text-gray-700 bg-gray-50 hover:border-blue-300">
                Search
            </button>
        </div>
    </div>
</template>

<script>
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiInformationVariantCircleOutline, mdiFilterOutline, mdiPlus, mdiClose, mdiChevronDown } from '@mdi/js';
import { useSearchStore } from '../stores/store.js';
import { toRefs } from 'vue';
import SearchBar from './SearchBar.vue';

export default {
    setup() {
        const searchStore = useSearchStore();
        const state = toRefs(searchStore);
        return {
            ...state,
        };
    },
    components: {
        SvgIcon,
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
            searchMode: "full",
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
        setExample(example) {
            this.inputValue = example;
        },
    },
};
</script>