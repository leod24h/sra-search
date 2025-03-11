<template>
  <el-select-v2 @input="e => $emit('input', e)" style="width: 100%" multiple filterable remote
    :remote-method="fetchAutocomplete" clearable :options="options" :loading="loading" placement="right"
    popper-class="autocompletePopup" placeholder="Please enter a keyword" class="desc-select-auto">
  </el-select-v2>
</template>
  
<script>
import axios from 'axios';
import { ElSelectV2 } from 'element-plus';

import { useSearchStore } from '../stores/store.js';
import { toRefs } from 'vue';

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
    ElSelectV2,

  },
  data() {
    return {
      options: [],
      loading: false,

    };
  },
  methods: {
    fetchAutocomplete(queryString) {
      console.log('Fetch!');
      const internalIP = window.location.hostname;
      const url = `https://${internalIP}:5000/autocomplete_desc`;
      axios
        .post(url, { descriptor: queryString }, {
          headers: {
            'Content-Type': 'application/json',
          },
        })
        .then((response) => {
          const suggestions = response.data.autocomplete_list;
          console.log(suggestions);
          this.options = suggestions.map((item) => ({
            value: item.descriptor_id,
            label: item.value,
          }));
          this.loading = false;
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },

  }
}

</script>
  