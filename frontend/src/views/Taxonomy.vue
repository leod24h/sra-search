<template>
  <div class="w-full mx-auto py-12 mb-10 px-12">
    <h2 class="text-2xl font-bold mb-1">Taxonomy Browser</h2>
    <p class="text-gray-600 text-sm mb-1">
      The Taxonomy Browser is a simple tool to explore the Sequence Read Archive (SRA) by taxonomy.
      It lets you browse the organism taxonomy and search SRA data for that organism, including all children of that
      level.
    </p>
    <p class="text-blue-600 text-sm mb-4">For example, selecting "Mammalia" search SRA data for all mammals, including
      children like "Primates" (e.g., humans, apes) and "Carnivora" (e.g., cats, dogs).
    </p>
    <div class="pb-2">
      <el-autocomplete v-model="taxonomy_organism" :fetch-suggestions="fetchAutocomplete" :trigger-on-focus="false"
        popper-class="autocompletePopup" clearable style="width:50%" placement="right"
        @select="handleTaxonomyOrganismSelect" @change="handleChange">
        <template #default="{ item }">
          <div class="flex items-center">
            {{ item.value }}
            <organism-wiki-tooltip :organism="item.value"></organism-wiki-tooltip>
          </div>
        </template>
      </el-autocomplete>
    </div>
    <el-tree ref="taxonomyTree" :key="treeKey" :load="loadNode" lazy show-checkbox @check-change="handleCheckChange">
      <template v-slot="{ node, data }">
        {{ data.name }}
        <organism-wiki-tooltip :organism="data.name"></organism-wiki-tooltip>
      </template>
    </el-tree>
    <div class="mt-6">
      <!-- <button @click="handleTaxonomySearch"
        class="bg-blue-500 text-white px-4 py-1 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
        Search
      </button> -->
      <div class="flex mt-4 mb-2 text-sm">
        <button @click="handleTaxonomySearch"
          class="mx-auto px-4 py-1 text-center border-2 border-gray-50 rounded-sm text-gray-700 bg-gray-50 hover:border-blue-300">
          Search
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import {
  ElInput, ElButton, ElForm, ElFormItem, ElCollapse, ElCollapseItem, ElDatePicker, ElCol, ElAutocomplete, ElCard, ElRow, ElImage, ElLink,
  ElTree, ElTreeSelect, ElPopover
} from 'element-plus';
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiInformationVariantCircleOutline } from '@mdi/js';
import OrganismWikiTooltip from '../components/OrganismWikiTooltip.vue';
import MapSelectionNoNumber from '../components/MapSelectNoNumber.vue';

export default {
  components: {
    ElAutocomplete,
    ElTree,
    SvgIcon,
    ElPopover,
    OrganismWikiTooltip,
    MapSelectionNoNumber,

  },
  data() {
    return {
      taxonomy_organism: 'root',
      taxonomy_organism_id: 1,
      handleTaxonomyOrganism: {
        selected_id: true
      },
      treeKey: 0,
      leafOrganismList: [],

    };
  },
  methods: {
    handleTaxonomyOrganismSelect(item) {
      this.taxonomy_organism_id = item.tax_id;
      this.handleTaxonomyOrganism.selected_id = true;
      this.treeKey++;
    },
    fetchAutocomplete(queryString, cb) {
      const internalIP = window.location.hostname;
      const url = `http://${internalIP}:5000/autocomplete_organism?query=${queryString}`;
      console.log(url);
      console.log(queryString);
      axios
        .get(url, {
          headers: {
            'Content-Type': 'application/json',
          },
        })
        .then((response) => {
          const suggestions = response.data;
          cb(suggestions);
        })
        .catch((error) => {
          console.error(error);
        });
    },
    loadNode(node, resolve) {
      console.log('Node level:', node.level);
      if (node.level == 0 && this.handleTaxonomyOrganism.selected_id) {
        return resolve([{ name: this.taxonomy_organism, 'organism_id': this.taxonomy_organism_id }]);
      }
      if (node.level > 0) {
        console.log(node);
        // const queryString = { 'organism_id': node.data.organism_id };
        // console.log(queryString);
        const internalIP = window.location.hostname;
        const url = `http://${internalIP}:5000/get_taxonomy_children_by_id?query=${node.data.organism_id}`;
        axios
          .get(url, {
            headers: {
              'Content-Type': 'application/json',
            },
          })
          .then((response) => {
            const childrenData = response.data;
            const reconstructedData = childrenData.map((child) => {
              return {
                name: child.scientific_name,
                organism_id: child.organism_id,
                isLeaf: true,
                // zones: child.zones || [], // Replace 'zones' with the appropriate field name
              };
            });
            console.log(reconstructedData);
            resolve(reconstructedData);
          })
          .catch((error) => {
            console.error(error);
          });
      }
    },
    getCheckedUnloadedNodes(node) {
      if (node.childNodes) {
        for (const childNode of Object.values(node.childNodes)) {
          this.getCheckedUnloadedNodes(childNode);
        }
      }
      if (node.checked && (!node.loaded || node.isLeaf)) {
        // const temp = {
        //   organism: node.data.name,
        //   organism_id: node.data.organism_id,
        // }
        this.leafOrganismList.push(node.data.organism_id);
        return;
      }
      return;
    },
    handleTaxonomySearch() {
      const tree = this.$refs.taxonomyTree;
      if (tree) {
        // console.log(tree.store.root.childNodes[0]);
        this.leafOrganismList = [];
        this.getCheckedUnloadedNodes(tree.store.root.childNodes[0]);
        console.log(this.leafOrganismList);
      }

      this.input_query = "";
      this.input_filters = [{
        operator: "AND",
        field: "organism",
        value: this.leafOrganismList,
        additional: "true",
      }];
      this.input_filters = JSON.stringify(this.input_filters);
      console.log(this.input_filters);
      
      this.$router.push({
        path: '/view',
        query: { search: this.input_query, filters: this.input_filters },
      });
    },



  }

}
</script>