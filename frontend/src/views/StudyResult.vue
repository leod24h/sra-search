<template>
  <div class="pb-10" v-loading="loading">
    <div class="px-10 py-5">

      <div class="flex justify-between items-center mb-4">
        <div class="flex gap-2">
          <el-popover placement="top" width="200" trigger="hover">
            <template #reference>
              <button
                class="border py-1 px-2 gap-1 rounded flex items-center text-xs hover:border-blue-200 hover:text-blue-500"
                @click="downloadStudyCSV">
                <svg-icon type="mdi" :path="mdiDownlaodCSV_path"></svg-icon>
                {{ isSelect ? 'Download selected studies' : 'Download all studies' }}
              </button>
            </template>
            Download the selected studies or all studies as a CSV file for your further analysis.
          </el-popover>

          <el-popover placement="top" width="200" trigger="hover">
            <template #reference>
              <button
                class="border py-1 px-2 gap-1 rounded flex items-center text-xs hover:border-blue-200 hover:text-blue-500"
                @click="downloadRelatedSampleCSV">
                <svg-icon type="mdi" :path="mdiDownlaodCSV_path"></svg-icon>
                {{ isSelect ? 'Download samples of selected studies' : 'Download samples of all studies' }}
              </button>
            </template>
            Download the sample of selected studies or all studies as a CSV file for your further analysis.
          </el-popover>
        </div>

        <el-popover placement="top" width="200" trigger="hover">
          <template #reference>
            <button
              class="border py-1 px-2 gap-1 rounded flex items-center text-xs hover:border-violet-200 hover:text-violet-500"
              :class="{ 'text-gray-400 border-gray-300 cursor-not-allowed': !isSelect }" :disabled="!isSelect"
              @click="toSampleSearch">
              <svg-icon type="mdi" :path="mdiNext_path"></svg-icon>
              Proceed to Sample Search
            </button>
          </template>
          Search for samples related to the selected SRA studies.
        </el-popover>
      </div>

      <el-table v-if="studySearchResults.length > 0" :data="studySearchResults" class="text-sm" ref="studyTable"
        :row-key="row => row.sra_study" @expand-change="handleRowExpand" @selection-change="handleSelectionChange">
        <!-- Expandable Column -->
        <el-table-column type="expand">
          <template #header>
            <el-popover placement="top" width="180" trigger="hover">
              <template #reference>
                <button @click="collapseAllRows" class="hover:text-blue-400">
                  <svg-icon type="mdi" :path="mdiArrowCollapseVertical_path"></svg-icon>
                </button>
              </template>
              Collapse expanded row.
            </el-popover>
          </template>
          <template #default="scope">
            <div class="p-4">
              <h3 class="font-bold text-lg text-gray-800">Related Samples</h3>

              <!-- Nested Table for Related Samples -->
              <el-table v-if="scope.row.samples && scope.row.samples.length > 0" :data="scope.row.samples"
                ref="sraTable"
                class="text-sm text-black rounded-[15px] shadow-[0_1px_3px_0_rgba(0,0,0,0.1),0_1px_2px_0_rgba(0,0,0,0.06)] mt-2"
                :cell-style="{ padding: '1.85vh 0.92vh 1.85vh 0.92vh' }"
                :header-cell-style="{ background: 'var(--very-light-1)', padding: '0.92vh' }"
                :header-row-style="{ position: 'sticky', top: '0' }" fit highlight-current-row>
                <!-- Dynamic Columns for Samples -->
                <el-table-column prop="acc" label="accession" min-width="140" max-width="180">
                  <template #default="{ row }">
                    <div class="text-custom-purple font-semibold">
                      {{ row.acc }}
                    </div>

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
              <div v-else class="text-gray-500 text-center">No samples found or still loading...</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column type="selection" width="55" />

        <!-- SRA Study Column -->
        <el-table-column prop="sra_study" label="SRA Study">
          <template #default="scope">
            <span class="text-custom-purple font-semibold text-base">
              {{ scope.row.sra_study }}
            </span>
          </template>
        </el-table-column>

        <!-- Study Abstract Column -->
        <el-table-column prop="study_abstract" label="Study Title & Abstract" min-width="350">
          <template #default="scope">
            <p class="text-gray-800 font-semibold text-lg break-normal whitespace-normal">
              {{ scope.row.study_title }}
            </p>
            <p class="text-gray-800 text-xs my-2 break-words">
              {{ scope.row.isExpand ? scope.row.study_abstract : '' }}
            </p>
          </template>
        </el-table-column>
      </el-table>

    </div>


  </div>
</template>

<script>
import axios from 'axios';
import {
  ElTable, ElTableColumn, ElTag, ElPopover, ElButton, ElPagination, ElLoading
} from 'element-plus';
import SvgIcon from '@jamescoyle/vue-icon';
import {
  mdiLinkVariant, mdiInformationVariantCircleOutline, mdiMapMarker, mdiSort,
  mdiTableArrowDown, mdiArrowRightThick, mdiArrowCollapseVertical
} from '@mdi/js';

import { useSearchStore } from '../stores/store.js';
import { toRefs } from 'vue';

import SearchBar from '../components/SearchBar.vue';
import OrganismWikiTooltip from '../components/OrganismWikiTooltip.vue';

export default {
  directives: {
    loading: ElLoading.directive,
  },
  setup() {
    const searchStore = useSearchStore();
    const state = toRefs(searchStore);
    return {
      ...state,
      searchForStudyFromAcc: searchStore.performSearch,
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
    ElPagination,
    OrganismWikiTooltip,

  },
  watch: {
    input_query: function (new_input_query, old_input_query) {
      console.log(`Query changed! New query: ${new_input_query}, Old query: ${old_input_query}`);
      this.loading = true;
      this.performStudySearch(new_input_query, this.search_mode);
    },

  },
  computed: {
    isSelect() {
      return this.selectedRows.length > 0; // True if any rows are selected
    },
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
      mdiNext_path: mdiArrowRightThick,
      mdiArrowCollapseVertical_path: mdiArrowCollapseVertical,

      loading: true,

      selectedRows: [],

    };
  },
  mounted() {

  },
  created() {
    this.input_query = this.$route.query.search;
    this.search_mode = this.$route.query.mode;

    this.performStudySearch(this.input_query, this.search_mode);

  },
  methods: {
    handleRowExpand(row) {
      row.isExpand = !row.isExpand; // Toggle the isExpand property
      // Check if samples are already fetched for this row
      if (row.samples) {
        return; // Samples already fetched, no need to fetch again
      }

      // Fetch related samples for this row's sra_study
      const internalIP = window.location.hostname;
      const apiUrl = `http://${internalIP}:5000/search_sample_by_study`;

      axios
        .get(apiUrl, {
          params: { query: row.sra_study },
        })
        .then((response) => {
          // Process the fetched samples
          row.samples = response.data.map((rowData) => {
            const rowObject = {};
            this.headers.forEach((header, index) => {
              rowObject[header] = rowData[index] || null; // Assign value or null if missing
            });
            return rowObject;
          });

          // Convert release date to human-readable format
          row.samples.forEach((result) => {
            const timestamp = result.releasedate;
            const date = new Date(timestamp * 1000); // Convert timestamp to milliseconds
            const humanDate = date.toLocaleDateString(); // Format the date in human-readable format
            result.releasedate_timestamp = timestamp;
            result.releasedate = humanDate; // Add the new property with human-readable date
          });

        })
        .catch((error) => {
          console.error(`Error fetching samples for ${row.sra_study}:`, error);
          row.samples = [];
        });
    },
    performStudySearch(query, mode) {
      const internalIP = window.location.hostname;
      const apiurl = `http://${internalIP}:5000/query_abstract`;
      var custom_params = {
        query: query,
      };
      if (mode == 'full') {
        custom_params.ft = 'true';
      } else {
        custom_params.ft = 'false';
      }
      axios
        .get(apiurl, {
          params: custom_params
        })
        .then((response) => {
          this.studySearchResults = response.data.map((row) => { // .slice(0, -1) to exclude the last element
            const rowObject = {};
            this.studyHeaders.forEach((header, index) => {
              rowObject[header] = row[index] || null; // Assign value or null if missing
            });
            // Add 'isExpand' property to each row
            rowObject.isExpand = false;
            return rowObject;
          });
          console.log("Search Results:", this.studySearchResults);

          this.loading = false;

        })
        .catch((error) => {
          // Handle errors
          console.error('Error fetching data:', error);
        });
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
    /**
     * Collapses all expanded rows in the table.
     */
    collapseAllRows() {
      const tableRef = this.$refs.studyTable; // Access the table via the ref

      if (tableRef) {
        // Iterate through all rows and collapse them
        this.studySearchResults.forEach((row) => {
          tableRef.toggleRowExpansion(row, false); // `false` collapses the row
        });
      } else {
        console.error("Table reference not found!");
      }
    },
    /**
    * Handles row selection changes.
    * @param {Array} selectedRows - Array of currently selected rows.
    */
    handleSelectionChange(selectedRows) {
      this.selectedRows = selectedRows;
    },
    /**
     * Converts selected or all rows to CSV and triggers download.
     */
    downloadStudyCSV() {
      // Step 1: Get the data to export
      const dataToExport = this.selectedRows.length > 0
        ? this.selectedRows // Export selected rows
        : this.studySearchResults; // Export all rows if no selection

      if (dataToExport.length === 0) {
        alert("No data available to download."); // Handle empty case
        return;
      }

      // Step 2: Convert data to CSV
      const headers = Object.keys(dataToExport[0]); // Extract headers from the first row
      const csvContent =
        headers.join(",") + // Add headers
        "\n" +
        dataToExport
          .map((row) =>
            headers.map((header) => JSON.stringify(row[header] || "")).join(",")
          )
          .join("\n"); // Add rows

      // Step 3: Create a Blob and trigger download
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const link = document.createElement("a");
      const url = URL.createObjectURL(blob);

      link.setAttribute("href", url);
      link.setAttribute(
        "download",
        this.selectedRows.length > 0 ? "selected_study.csv" : "all_study.csv"
      );
      link.style.display = "none";

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      console.log("CSV download triggered!");
    },
    innerDownlaodSampleCSV() {
      // Step 3: Convert data to CSV
      var dataToExport = this.selectedRows.length > 0
        ? this.selectedRows // Export selected rows
        : this.studySearchResults; // Export all rows if no selection

      // Get the samples from the selected rows if there is row.samples
      dataToExport = dataToExport.map(row => {
        if (row.samples && row.samples.length > 0) {
          return row.samples.map(sample => ({
            ...sample,
            sra_study: row.sra_study, // Add the sra_study to each sample
          }));
        } else {
          return [];
        }
      }).flat();

      const headers = Object.keys(dataToExport[0]); // Extract headers from the first row
      const csvContent =
        headers.join(",") + // Add headers
        "\n" +
        dataToExport
          .map((row) =>
            headers.map((header) => JSON.stringify(row[header] || "")).join(",")
          )
          .join("\n"); // Add rows

      // Step 4: Create a Blob and trigger download
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const link = document.createElement("a");
      const url = URL.createObjectURL(blob);
      link.setAttribute("href", url);
      link.setAttribute(
        "download",
        this.selectedRows.length > 0 ? "selected_samples.csv" : "all_samples.csv"
      );
      link.style.display = "none";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      console.log("CSV download triggered!");
    },
    downloadRelatedSampleCSV() {
      // Step 1: Get the data to export
      var dataToExport = this.selectedRows.length > 0
        ? this.selectedRows // Export selected rows
        : this.studySearchResults; // Export all rows if no selection

      if (dataToExport.length === 0) {
        alert("No data available to download."); // Handle empty case
        return;
      }

      // Step2: Fetch missing samples for selected SRA studies
      // Check which sra_study has empty samples
      const sraStudiesWithEmptySamples = dataToExport.filter(row => !row.samples || row.samples.length === 0);

      const sraStudyValues = sraStudiesWithEmptySamples.map(row => row.sra_study).join(", "); // Join selected SRA studies
      console.log("Selected SRA Studies with empty samples:", sraStudyValues);

      if (sraStudiesWithEmptySamples.length > 0) {
        const internalIP = window.location.hostname;
        const apiUrl = `http://${internalIP}:5000/fetch_study_from_multiple_study`;

        axios
          .get(apiUrl, {
            params: { query: sraStudyValues },
          })
          .then((response) => {
            var samples_tmp = response.data.map((rowData) => {
              const rowObject = {};
              this.headers.forEach((header, index) => {
                rowObject[header] = rowData[index] || null; // Assign value or null if missing
              });
              return rowObject;
            });

            // group samples by sra_study
            const groupedSamples = {};
            samples_tmp.forEach(sample => {
              const sra_study = sample.sra_study;
              if (!groupedSamples[sra_study]) {
                groupedSamples[sra_study] = [];
              }
              groupedSamples[sra_study].push(sample);
            });

            // Assign samples to the corresponding studySearchResults
            this.studySearchResults.forEach(study => {
              const sra_study = study.sra_study;
              if (groupedSamples[sra_study]) {
                study.samples = groupedSamples[sra_study];
              }
            });

            this.innerDownlaodSampleCSV(); // Call the inner function to download the CSV

          });

      } else {
        this.innerDownlaodSampleCSV(); // Call the inner function to download the CSV

      }

    },
    toSampleSearch() {
      console.log("Route to SampleSearch");
      console.log("Selected rows:", this.selectedRows);
      const selectedSraStudies = this.selectedRows.map(row => row.sra_study).join(", ");
      console.log("Selected SRA Studies:", selectedSraStudies);

      this.filters = [{ operator: "AND", field: "acc", value: selectedSraStudies, additional: "" }];

      // route to SampleSearch
      this.$router.push({
        path: '/sample',
      });

    }
  },
}

</script>