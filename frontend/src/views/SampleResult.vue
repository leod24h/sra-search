<template>
  <div class="pb-10" v-loading="loading">
    <div class="mx-10 mt-4">
      <!-- Search Bar -->
      <search-bar class="w-4/5" v-model="inputValue" @search="handleSearch"></search-bar>
      <!-- Statistics Section -->
      <div class="bg-white border rounded-lg mt-5 px-2 py-2" :class="{ 'hover:bg-gray-50': !isExpanded }">
        <!-- Header with Minimize/Expand -->
        <div class="flex justify-between items-center cursor-pointer" @click="isExpanded = !isExpanded">
          <h2 class="text-lg font-semibold text-gray-700">Statistics</h2>
          <button class="text-gray-500 hover:text-gray-700">
            <svg v-if="isExpanded" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>

        <!-- Expandable Content -->
        <div v-if="isExpanded" class="mt-4">

          <!-- Chart Grid -->
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2 mt-4">
            <!-- Doughnut Chart Section -->
            <div class="h-64 bg-gray-50 p-4 rounded-md shadow-sm">
              <p class="text-sm font-medium text-gray-600">Count by Organism</p>
              <DoughnutChart class="mx-auto pb-2" :data="chartData" :options="{
                responsive: true,
                plugins: {
                  legend: {
                    display: false,
                  },
                },
              }" />
            </div>

            <!-- Bar Chart Section -->
            <div class="h-64 bg-gray-50 p-4 rounded-md shadow-sm">
              <p class="text-sm font-medium text-gray-600 mb-2">Count by Month</p>
              <Bar class="pb-2" :data="chartData_time" :options="{
                responsive: true,
                plugins: {
                  legend: {
                    display: false,
                  },
                },
              }" />
            </div>
          </div>

          <!-- Map Visualization Section -->
          <div class="mt-6">
            <p class="text-sm font-medium text-gray-600 mb-2">Map Visualization</p>
            <div id="mapVisualization_plot" class="h-64 bg-gray-50 rounded-md shadow-sm"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="px-10 py-5">
      <div class="mb-2">
        <el-popover placement="top" width="200" trigger="hover">
          <template #reference>
            <button
              class="border py-1 px-2 gap-1 rounded flex items-center text-xs hover:border-blue-200 hover:text-blue-500"
              @click="downloadSampleCSV">
              <svg-icon type="mdi" :path="mdiDownlaodCSV_path"></svg-icon>
              Download all samples
            </button>
          </template>
          Download all samples of <b class="text-red-500">this page</b> as a CSV file for your further analysis.
        </el-popover>
      </div>

      <div class="flex items-center">
        <span class="text-[15px] text-gray-600">Total {{ searchResultsTotal }}</span>
        <el-pagination :page-size="pageSize" :total="allSearchResults.length" :current-page="currentPage"
          layout="prev, pager, next, jumper" @current-change="handlePagination" />
        <span class="text-[15px] text-gray-600">Page Size {{ pageSize }}</span>
      </div>
      <el-table ref="sraTable" :data="paginatedResults"
        class="text-sm text-black rounded-[15px] shadow-[0_1px_3px_0_rgba(0,0,0,0.1),0_1px_2px_0_rgba(0,0,0,0.06)] mt-2"
        :cell-style="{ padding: '1.85vh 0.92vh 1.85vh 0.92vh' }"
        :header-cell-style="{ background: 'var(--very-light-1)', padding: '0.92vh' }"
        :header-row-style="{ position: 'sticky', top: '0' }" fit highlight-current-row>
        <el-table-column type="selection" width="55" v-if="showSelectForDownloadCSV" />
        <el-table-column prop="acc" label="accession" min-width="140" max-width="180">
          <template #default="{ row }">
            <el-popover placement="right" trigger="hover" width="40vw" @show="fetchStudy(row)">
              <template #reference>
                <el-button color="#5559a6" plain @click="toMetadatPage(row.acc)">{{ row.acc }}</el-button>
              </template>
              <span class="text-custom-purple text-[1rem]">Study title</span>
              <p class="text-custom-dark-purple text-[0.65rem]">{{ row.study_title }}</p>
              <span class="text-custom-purple text-[1rem]">Study abstract</span>
              <p class="text-custom-dark-purple font-[0.65rem]">{{ row.study_abstract }}</p>
              <div class="mt-2">
                <table class="table-auto border-collapse border border-gray-300 w-full text-left">
                  <tbody>
                    <tr class="border-b">
                      <td class="px-2 py-1 font-bold">SRA Run</td>
                      <td class="px-2 py-1">
                        <a :href="'https://trace.ncbi.nlm.nih.gov/Traces/?view=run_browser&acc=' + row.acc + '&display=metadata'"
                          class="text-blue-500 hover:underline">
                          {{ row.acc }}
                        </a>
                      </td>
                    </tr>
                    <tr class="border-b">
                      <td class="px-2 py-1 font-bold">SRA Experiment</td>
                      <td class="px-2 py-1">
                        <a :href="'https://www.ncbi.nlm.nih.gov/sra/' + row.experiment"
                          class="text-blue-500 hover:underline">
                          {{ row.experiment }}
                        </a>
                      </td>
                    </tr>
                    <tr class="border-b">
                      <td class="px-2 py-1 font-bold">SRA Sample</td>
                      <td class="px-2 py-1">
                        <a :href="'https://www.ncbi.nlm.nih.gov/biosample/' + row.biosample"
                          class="text-blue-500 hover:underline">
                          {{ row.biosample }}
                        </a>
                      </td>
                    </tr>
                    <tr>
                      <td class="px-2 py-1 font-bold">SRA Study</td>
                      <td class="px-2 py-1">
                        <a :href="'https://www.ncbi.nlm.nih.gov/bioproject/' + row.bioproject"
                          class="text-blue-500 hover:underline">
                          {{ row.bioproject }}
                        </a>
                        |
                        <a :href="'https://trace.ncbi.nlm.nih.gov/Traces/?view=study&acc=' + row.sra_study"
                          class="text-blue-500 hover:underline">
                          {{ row.sra_study }}
                        </a>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <!-- <svg-icon type="mdi"
                  :path="mdiLink_path"></svg-icon> -->
                <!-- <div>
                  SRA Run: 
                  <a :href="'https://www.ncbi.nlm.nih.gov/sra/' + row.acc">
                      {{ row.acc }}
                    </a>
                </div>
                <div>
                  SRA Experiment: 
                  <a :href="'https://www.ncbi.nlm.nih.gov/sra/' + row.acc">
                      {{ row.experiment }}
                    </a>
                </div>
                <div>
                  SRA Sample: 
                  <a :href="'https://www.ncbi.nlm.nih.gov/sra/' + row.acc">
                      {{ row.biosample }}
                    </a>
                </div>
                <div>
                  SRA Study:  
                  <a :href="'https://www.ncbi.nlm.nih.gov/bioproject/' + row.bioproject">{{ row.bioproject}}</a> 
                  | 
                  <a :href="'https://trace.ncbi.nlm.nih.gov/Traces/?view=study&acc=' + row.sra_study">{{ row.sra_study }}</a>
                </div> -->
              </div>
            </el-popover>
            <br>
          </template>
        </el-table-column>
        <el-table-column prop="organism" label="organism" ref="organismColumn" min-width="150">
          <template #default="{ row }">
            <div style="display: inline-flex; align-items: center;">
              <span>{{ row.organism }}</span>
              <OrganismWikiTooltip :organism="row.organism"></OrganismWikiTooltip>
            </div>
          </template>

        </el-table-column>
        <!-- <el-table-column prop="instrument" label="instrument" min-width="150" /> -->
        <el-table-column prop="center_name" label="center" min-width="150" />

        <el-table-column label="country" min-width="150">
          <template #header>
            <div>
              country
            </div>
          </template>
          <template #default="{ row }">
            <div>
              <div v-if="row.country && checkValidCountry(row.country)">{{ row.country }}<br></div>

              <div v-if="row.latitude">
                <el-popover :width="450">
                  <template #reference>
                    <svg-icon type="mdi" :path="mdiMap_path" class="info-icon-popover"></svg-icon>
                  </template>
                  Collection latitude and longitude: {{ row.latitude }}, {{ row.longitude }}
                </el-popover>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="releasedate" label="release date" min-width="150">
          <template #header>
            releasedate
            <span class="caret-wrapper"><i class="sort-caret ascending" @click="sortByDate('ASC')"></i><i
                class="sort-caret descending" @click="sortByDate('DESC')"></i></span>
          </template>
        </el-table-column>
        <el-table-column label="sample attributes" min-width="300" max-width="300">
          <template #default="{ row }">
            <span v-for="(attribute, index) in splitAttributes(row.attributes)" :key="index">
              <el-tag v-if="attribute.key" class="attribute-tag">
                {{ attribute.key }}
              </el-tag>
              <span style="font-size: 0.7rem;"><br>{{ attribute.value }}<br></span>
            </span>
          </template>
        </el-table-column>
      </el-table>
      <div class="flex items-center mt-4">
        <span class="text-[15px] text-gray-600">Total {{ searchResultsTotal }}</span>
        <el-pagination :page-size="pageSize" :total="allSearchResults.length" :current-page="currentPage"
          layout="prev, pager, next, jumper" @current-change="handlePagination" />
        <span class="text-[15px] text-gray-600">Page Size {{ pageSize }}</span>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios';
import {
  ElTable, ElTableColumn, ElTag, ElPopover, ElButton, ElPagination, ElText, ElRow, ElCol, ElLoading, ElCheckboxButton,
} from 'element-plus';
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiLinkVariant, mdiInformationVariantCircleOutline, mdiMapMarker, mdiSort, mdiTableArrowDown, } from '@mdi/js';

import { Chart as ChartJS, ArcElement, Tooltip, Legend, Title, BarElement, CategoryScale, LinearScale } from 'chart.js';
import { Doughnut } from 'vue-chartjs';
import { Bar } from 'vue-chartjs';
import Plotly from 'plotly.js-dist';

import { useSearchStore } from '../stores/store.js';
import { toRefs } from 'vue';

import SearchBar from '../components/SearchBar.vue';
import OrganismWikiTooltip from '../components/OrganismWikiTooltip.vue';
import DownloadCSV from '../components/DownloadCSV.vue';

ChartJS.register(ArcElement, Tooltip, Legend, Title, BarElement, CategoryScale, LinearScale);

export default {
  directives: {
    loading: ElLoading.directive,
  },
  setup() {
    const searchStore = useSearchStore();
    const state = toRefs(searchStore);
    return {
      ...state,
      // searchForStudyFromAcc: searchStore.performSearch,
    };
  },
  components: {
    SearchBar,
    ElTable,
    ElTableColumn,
    ElTag,
    ElPopover,
    ElButton,
    SvgIcon,
    DoughnutChart: Doughnut,
    Bar,
    ElPagination,
    ElText,
    ElRow,
    ElCol,
    OrganismWikiTooltip,
    DownloadCSV,
    ElCheckboxButton,

  },
  watch: {
    input_query: function (new_input_query, old_input_query) {
      console.log(`Query changed! New query: ${new_input_query}, Old query: ${old_input_query}`);
      this.loading = true;
      this.performSearchWithFilters(new_input_query, []);
    },
    isExpanded(newValue) {
      // Render the map visualization when the section is expanded
      if (newValue) {
        setTimeout(() => {
          // Call the mapVisualization method after a 100ms delay
          this.mapVisualization(this.searchResults);
        }, 100);
      }
    },
  },
  computed: {
    paginatedResults() {
      const start = (this.currentPage - 1) * this.pageSize;
      const end = start + this.pageSize;
      return this.allSearchResults.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.allSearchResults.length / this.pageSize);
    }
  },
  data() {
    return {
      inputValue_raw: '',
      inputValue: '',
      mdiLink_path: mdiLinkVariant,
      mdiInfo_path: mdiInformationVariantCircleOutline,
      mdiMap_path: mdiMapMarker,
      mdiSort_path: mdiSort,
      mdiDownlaodCSV_path: mdiTableArrowDown,
      showPopupCard_bool: false,
      chartData: {
        labels: [],
        datasets: [
          {
            data: [],
            backgroundColor: [],
          },
        ],
      },
      chartData_time: {
        labels: [],
        datasets: [
          {
            backgroundColor: '#f87979',
            data: [],
          },
        ],
      },
      loading: true,
      organism_list: [],
      isExpanded: false,
      currentPage: 1,
      pageSize: 20, // Change from 100 to 20
      currentPage: 1,
      allSearchResults: [], // Store all results

    };
  },
  mounted() {

  },
  created() {
    this.input_query = this.$route.query.search;
    if (this.$route.query.filters) {
      this.input_filters = JSON.parse(this.$route.query.filters);
    }
    console.log(this.input_query);
    console.log(this.input_filters);
    if (this.input_filters.length > 0) {
      console.log("Advanced search");
      this.performSearchWithFilters(this.input_query, this.input_filters);
    } else {
      console.log("Simple search");
      this.performSearchWithFilters(this.input_query, []);
    }

  },
  methods: {
    handleSearch() {
      if (this.inputValue.trim()) {
        this.$router.push({
          path: '/sample_result',
          query: { search: this.inputValue.trim() },
        });
        this.input_query = this.inputValue.trim();
      }
    },
    toMetadatPage(acc) {
      this.$router.push({ name: 'Metadata', params: { 'accession': acc } });
    },
    performSearchWithFilters(query, filters) {
      const internalIP = window.location.hostname;
      const apiurl = `http://${internalIP}:5000/query_with_filter`;
      var custom_params = {
        query: query,
      };
      if (filters.length > 0) {
        custom_params.filters = JSON.stringify(filters);
      }
      axios
        .get(apiurl, {
          params: custom_params
        })
        .then((response) => {
          // console.log(response.data);
          this.searchResultsTotal = response.data[response.data.length - 1];
          console.log("Total search results: " + this.searchResultsTotal);
          this.searchResultsCount = response.data.length - 1;

          // Store all results
          this.allSearchResults = response.data.slice(0, -1).map((row) => {
            const rowObject = {};
            this.headers.forEach((header, index) => {
              rowObject[header] = row[index] || null;
            });
            return rowObject;
          });

          // Process dates for all results
          this.allSearchResults.forEach(function (result) {
            var timestamp = result.releasedate;
            var date = new Date(timestamp * 1000);
            var humanDate = date.toLocaleDateString();
            result.releasedate_timestamp = timestamp;
            result.releasedate = humanDate;
          });

          // Reset to first page
          this.currentPage = 1;

          // Update charts with all data
          const organismCounts = this.countOrganisms(this.allSearchResults);
          this.chartData = {
            labels: Object.keys(organismCounts),
            datasets: [{
              data: Object.values(organismCounts),
              backgroundColor: ["#efe1e6", "#d2b7d2", "#c7cbd9", "#bfcfd2", "#cfe3db", "#dce6d3", "#ede9ce"],
            }],
          };
          this.countSampleByMonth_visualization(this.allSearchResults);
          this.loading = false;
        })
        .catch((error) => {
          // Handle errors
          console.error('Error fetching data:', error);
        });
    },
    countOrganisms(data) {
      const organismCounts = {};
      for (const entry of data) {
        const organism = entry.organism;
        organismCounts[organism] = (organismCounts[organism] || 0) + 1;
      }

      // Sort the organismCounts object by count in descending order
      const sortedOrganismCounts = Object.entries(organismCounts)
        .sort((a, b) => b[1] - a[1])
        .reduce((obj, [key, value]) => {
          obj[key] = value;
          return obj;
        }, {});

      this.organism_list = Object.entries(sortedOrganismCounts).map(([key, value]) => ({
        text: `${key} (${value})`,
        value: key
      }));
      return sortedOrganismCounts;
    },
    countSampleByMonth_visualization(searchResultData) {
      const dataCountsByMonth = {};

      for (var json of searchResultData) {
        var timestamp = parseInt(json.releasedate_timestamp) * 1000;
        var date = new Date(timestamp);
        var month = `${date.getFullYear()}-${date.getMonth() + 1}`;

        if (dataCountsByMonth[month]) {
          dataCountsByMonth[month]++;
        } else {
          dataCountsByMonth[month] = 1;
        }
      }

      const sortedMonths = Object.keys(dataCountsByMonth).sort(); // Sort the months

      this.chartData_time = {
        labels: sortedMonths,
        datasets: [
          {
            backgroundColor: [
              "rgba(252, 172, 188, 0.9)",
              "rgba(255, 227, 171, 0.9)",
              "rgba(127, 203, 241, 0.9)",
              "rgba(255, 202, 162, 0.9)",
              "rgba(147, 219, 218, 0.9)",
              "rgba(199, 172, 252, 0.9)",
              "rgba(224, 226, 225, 0.9)"
            ],
            data: sortedMonths.map(month => dataCountsByMonth[month]) // Use sortedMonths to map the corresponding data values
          }
        ]
      };
    },
    mapVisualization(searchResultData) {
      const colors = [
        '#bebada', '#fdb462', '#fb8072', '#d9d9d9', '#bc80bd',
        '#b3de69', '#8dd3c7', '#80b1d3', '#fccde5', '#ffffb3'
      ];

      const data = searchResultData
        .filter(json => (json.latitude !== null && json.longitude !== null)
          || (json.country_lat !== null && json.country_lng !== null)
          || (json.inferred_lat !== null && json.inferred_lng !== null))
        .map((json, index) => {
          let lat, lon;
          if (json.latitude !== null && json.longitude !== null) {
            lat = json.latitude;
            lon = json.longitude;
          } else if (json.country_lat !== null && json.country_lng !== null) {
            lat = json.country_lat;
            lon = json.country_lng;
          } else if (json.inferred_lat !== null && json.inferred_lng !== null) {
            lat = json.inferred_lat;
            lon = json.inferred_lng;
          }
          return {
            type: 'scattergeo',
            mode: 'markers',
            text: [json.inferred_country],
            lon: [lon],
            lat: [lat],
            marker: {
              size: 7,
              color: colors[index % colors.length],
              line: {
                width: 1
              },
            },
            name: "",
          };
        });

      var layout = {
        // title: 'Distribution among the world',
        showlegend: false,
        geo: {
          scope: 'world',
          resolution: 50,
          showland: true,
          landcolor: 'rgb(244,233,244)',
          showlake: true,
          lakecolor: 'rgb(0, 255, 0)',
          countrycolor: 'rgb(217,217,217)',
          countrywidth: 0.5,
          subunitwidth: 0.5
        }, margin: {
          l: 0,
          r: 0,
          b: 0,
          t: 0,
          pad: 0,
        },
      };

      Plotly.newPlot('mapVisualization_plot', data, layout, { displayModeBar: false, });
    },
    handlePagination(val) {
      console.log(`current page: ${val}`);
      this.currentPage = val;
      // Remove API call - just change the page number
      // The computed property will handle showing the right data
    },
    sortByDate(order) {
      if (order == "ASC") {
        this.allSearchResults.sort((a, b) => { return a.releasedate_timestamp - b.releasedate_timestamp });
      } else {
        this.allSearchResults.sort((a, b) => { return b.releasedate_timestamp - a.releasedate_timestamp });
      }
      // Reset to first page after sorting
      this.currentPage = 1;
    },
    fetchStudy(row) {
      const sra_study = row.sra_study;

      if (row.study_title && row.study_abstract) {
        return;
      }

      const internalIP = window.location.hostname;
      const apiurl = `http://${internalIP}:5000/fetch_study`;
      const custom_params = {
        query: sra_study,
      };

      axios
        .get(apiurl, { params: custom_params })
        .then((response) => {

          row.study_title = response.data[0][0];
          row.study_abstract = response.data[0][1];

        })
        .catch((error) => {
          console.error('An error occurred:', error);
        });

    },
    downloadSampleCSV() {
      // Prepare the CSV content
      const headers = this.headers;
      const csvContent =
        headers.join(",") + // Add headers
        "\n" +
        this.searchResults
          .map((row) =>
            headers.map((header) => JSON.stringify(row[header] || "")).join(",")
          )
          .join("\n"); // Add rows
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.setAttribute('download', `samples_page${this.currentPage}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      console.log("CSV download triggered!");

    }
  },
}

</script>

<style scoped>
a:link {
  color: var(--purple-1);
  background-color: transparent;
  text-decoration: none;
}

a:visited {
  color: var(--purple-1);
  background-color: transparent;
  text-decoration: none;
}

a:hover {
  color: var(--purple-light-2);
  background-color: transparent;
  text-decoration: none;
}
</style>
