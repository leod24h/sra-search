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
        <!-- <div class="mt-4 mb-4 text-gray-500 text-xs flex items-center">
            <div class=" flex flex-row space-x-2 ">
                <div class="rounded px-2 py-1 cursor-pointer text-gray-800 bg-gray-50" @click="setExample('Malaysian forest animal')">
                    Malaysian forest animal
                </div>
                <div class="rounded px-2 py-1 cursor-pointer text-gray-800 bg-gray-50" @click="setExample('ESBL')">
                    ESBL
                </div>
            </div>
        </div> -->

        <!-- Radio button -->
        <div class="text-xs w-fit">
            <div class="flex flex-row items-center gap-2 px-2 py-3">
                <h2 class="text-md font-semibold text-gray-600">Search mode</h2>
                <label class="flex items-center cursor-pointer">
                    <input type="radio" value="full" v-model="searchMode" class="hidden peer" />
                    <div
                        class="px-3 py-1 rounded border bg-gray-100 text-gray-600 font-medium transition-all peer-checked:text-blue-500 peer-checked:bg-blue-100 text-center flex-1">
                        Full-text search
                    </div>
                </label>

                <label class="flex items-center cursor-pointer">
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

        <div class="text-gray-800">
            <div class="text-sm font-semibold text-gray-600 mb-2">
                Examples
            </div>
            <div class="w-full flex text-xs text-gray-800">
                <table class="w-4/5 md:w-1/2 border border-gray-200 text-left">
                    <tbody>
                        <tr v-for="(row, index) in examples" :key="index" @click="handleExampleClick(row)"
                            class="cursor-pointer hover:bg-orange-50">
                            <td class="border border-gray-300 px-2 py-2">{{ row.query }}</td>
                            <td class="border border-gray-300 px-2 py-2">{{ row.mode }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
import SvgIcon from '@jamescoyle/vue-icon';
import { ElTable, ElTableColumn, ElPopover } from 'element-plus';
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
        ElTable,
        ElTableColumn,
        ElPopover,
    },
    data() {
        return {
            inputValue: "",
            searchMode: "full",
            examples: [
                {
                    'query': 'ESBL',
                    'mode': 'full',
                },
                {
                    'query': 'Malaysian forest animal',
                    'mode': 'semantic',
                },
            ]
        };
    },
    methods: {
        handleSearch() {
            this.input_query = this.inputValue.trim();
            console.log(this.input_query, this.searchMode);

            this.$router.push({
                path: '/study_result',
                query: { search: this.input_query, mode: this.searchMode },
            });
        },
        handleExampleClick(row) {
            // Set inputValue and searchMode based on the clicked row
            this.inputValue = row.query;
            this.searchMode = row.mode;
        },
    },
};
</script>

<style>
/* .el-table__body tr:hover>td {
    background-color: #fff7ed !important;
} */
</style>