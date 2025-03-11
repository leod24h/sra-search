<template>
  <el-select-v2 @input="e => $emit('input', e)" style="width: 100%" multiple filterable remote autocomplete=""
    :remote-method="fetchAutocomplete" clearable :options="options" :loading="loading" placement="right"
    popper-class="autocompletePopup" default-first-option placeholder="Please enter a keyword"
    @keydown.enter="handleOrganismEnter">
    <template #default="{ item }">
      <div style="display: flex; align-items: center;">
        {{ item.label }}
        <organism-wiki-tooltip :organism="item.label"></organism-wiki-tooltip>
      </div>
    </template>
  </el-select-v2>
</template>

<script>
import axios from 'axios';
import { ElSelectV2 } from 'element-plus';

import { useSearchStore } from '../stores/store.js';
import { toRefs } from 'vue';

import OrganismWikiTooltip from './OrganismWikiTooltip.vue';

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
    OrganismWikiTooltip,

  },
  data() {
    return {
      options: [],
      loading: false,

    };
  },
  methods: {
    fetchAutocomplete(queryString) {
      const internalIP = window.location.hostname;
      const url = `http://${internalIP}:5000/autocomplete_organism?query=${queryString}`;
      axios
        .get(url, {
          headers: {
            'Content-Type': 'application/json',
          },
        })
        .then((response) => {
          const suggestions = response.data;
          console.log(suggestions);
          this.options = suggestions.map((item) => ({
            value: item.tax_id,
            label: item.value,
          }));
          this.loading = false;
        })
        .catch((error) => {
          console.error(error);
          this.loading = false;
        });
    },
    handleOrganismEnter() {
      const inputValue = event.target.value;
      console.log('Current input value:', inputValue);
    }

  }
}

</script>

<style>
.el-select-dropdown__option-item {
  font-size: var(--el-font-size-base);
  padding: 0 20px;
  margin: 0;
}

.el-vl__wrapper {
  position: relative;
  width: auto;
}

.el-select-dropdown__list {
  min-width: 500px !important;
}
</style>