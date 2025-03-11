
<template>

    <el-button color="rgb(126, 175, 205)" plain @click="downloadCSV">
      <svg-icon type="mdi" :path="mdiDownlaodCSV_path" style="padding-right: 5px;"></svg-icon>{{ isSelect ? 'Download CSV by Select' : 'Download CSV' }}
    </el-button>

</template>


<script>
import { ElButton } from 'element-plus';
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiTableArrowDown } from '@mdi/js';

import { useSearchStore } from '../stores/store.js';
import { toRefs } from 'vue';

export default {
  setup() {
    const searchStore = useSearchStore();
    const state = toRefs(searchStore);
    return {
      ...state,
    };
  },
  components: {
    ElButton,
    SvgIcon,

  },
  data() {
    return {
      mdiDownlaodCSV_path: mdiTableArrowDown,
    };
  },
  props: {
    isSelect: {
      type: Boolean
    }
  },
  methods: {
    convertToCSV(data) {
      const header = Object.keys(data[0]).join(',') + '\n';
      const rows = data.map(obj => Object.values(obj).join(',')).join('\n');
      return header + rows;
    },
    downloadCSV() {
      // Specify the fields to include in the CSV
      const fields = ['acc', 'bioproject', 'organism', 'category',];

      // Filter the table data based on the selected fields
      const filteredData = this.searchResults.map(result => {
        const filteredResult = {};
        fields.forEach(field => {
          filteredResult[field] = result[field];
        });
        return filteredResult;
      });

      // Convert the filtered data to CSV format
      const csvData = this.convertToCSV(filteredData);

      // Create a download link
      const link = document.createElement('a');
      link.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvData));
      link.setAttribute('download', 'table.csv');
      link.style.display = 'none';

      // Add the link to the DOM and trigger the download
      document.body.appendChild(link);
      link.click();

      // Clean up
      document.body.removeChild(link);
    },

  }
}

</script>

<style></style>