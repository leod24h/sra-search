<template>
  <div style="padding: 4vh 8vw 10vh 8vw;">
    <el-row :gutter="50">
      <el-col :xs="24" :sm="24" :md="18">
        <div v-if="searchResults[0]">
          <div> {{ accession }} </div>
          <div style="padding: 1rem 0;">
            <el-descriptions :column="1" :size="size" border>
              <el-descriptions-item>
                <template #label>
                  <div>
                    Organism
                  </div>
                </template>
                {{ searchResults[0]['organism'] }}
              </el-descriptions-item>
              <el-descriptions-item>
                <template #label>
                  <div>
                    Release date
                  </div>
                </template>
                {{ timestampToHumanDate(searchResults[0]['releasedate_timestamp']) }}
              </el-descriptions-item>
              <el-descriptions-item v-if="searchResults[0]['collectiondate_timestamp']">
                <template #label>
                  <div>
                    Collection date
                  </div>
                </template>
                {{ timestampToHumanDate(searchResults[0]['collectiondate_timestamp']) }}
              </el-descriptions-item>
              <el-descriptions-item>
                <template #label>
                  <div>
                    Center
                  </div>
                </template>
                {{ searchResults[0]['center_name'] }}
              </el-descriptions-item>
              <el-descriptions-item>
                <template #label>
                  <div>
                    Geographical information
                  </div>
                </template>
                <div v-if="searchResults[0].country">{{ searchResults[0].country }}</div>
                <div v-else-if="searchResults[0].inferred_country">
                  Inferred: {{ searchResults[0].inferred_country }}
                  <el-popover :width="200">
                    <template #reference>
                      <svg-icon type="mdi" :path="mdiInfo_path" class="info-icon-popover"></svg-icon>
                    </template>
                    Inferred from study.
                  </el-popover>
                </div>
                <div v-if="searchResults[0].latitude">
                  <el-popover :width="450">
                    <template #reference>
                      <svg-icon type="mdi" :path="mdiMap_path" class="info-icon-popover"></svg-icon>
                    </template>
                    Collection latitude and longitude: {{ searchResults[0].latitude }}, {{ searchResults[0].longitude }}
                  </el-popover>
                </div>
              </el-descriptions-item>
              <el-descriptions-item>
                <template #label>
                  <div>
                    Attributes
                  </div>
                </template>
                <span v-for="(attribute, index) in splitAttributes(searchResults[0]['attributes'])" :key="index">
                  <el-tag v-if="attribute.key" class="attribute-tag">
                    {{ attribute.key }}
                  </el-tag>
                  <span><br>{{ attribute.value }}<br></span>
                </span>
              </el-descriptions-item>
            </el-descriptions>
          </div>
          <div> Related Study</div>
          <div style="padding: 1rem 0;">
            <el-descriptions :column="1" :size="size" border>
              <template v-for="(key) in Object.keys(studyColDict)">
                <el-descriptions-item>
                  <template #label>
                    <div>
                      {{ studyColDict[key] }}
                    </div>
                  </template>
                  {{ searchResults[0][key] }}
                </el-descriptions-item>
              </template>
            </el-descriptions>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :md="6">
        <div v-if="searchResults">
          <div v-if="getMapUrl()">
            <div>
              <div style="display: flex; align-items: center;">
                <svg-icon type="mdi" :path="mdiImageMap_path" class="mr-2" color="var(--el-color-primary)"></svg-icon>
                Map
              </div>
            </div>
            <div style="padding: 1rem 0;">
              <iframe width="400" height="360" style="border:0" loading="lazy" allowfullscreen
                referrerpolicy="no-referrer-when-downgrade" :src="getMapUrl()">
              </iframe>
            </div>
          </div>

          <!-- <div style="border-color: var(--green-1);">
            <div style="display: flex; align-items: center;">
              <img src="MeSH-Tree.png" class="mr-2 h-5" />
              MeSH Term
            </div>
          </div>

          <div class="px-2">
            <div style="font-weight: 400; line-height: 35px; font-size: 16px;">
              <div v-for="(terms, category) in groupedMeshTerm">
                <span style="color: var(--green-2);" class="background-rounded">{{ categoryDict[category] }}</span>
                <div v-for="term in terms">
                  <div style="display: flex; align-items: center;">
                    <svg-icon type="mdi" :path="mdiCircle_path" color="var(--green-1)"></svg-icon>
                    <span style="padding-left: 10px; ">
                      {{ term.descriptor_name }}
                    </span>
                    <el-popover :width="350" placement="right">
                      <template #reference>
                        <svg-icon type="mdi" :path="mdiInfo_path" class="info-icon-popover"
                          color="var(--green-1)"></svg-icon>
                      </template>
                      <div style="padding: 0.5rem; ">
                        <span style="color: var(--green-2);"><b><u>{{ term.descriptor_name }}</u></b></span><br>
                        <p>{{ term.definitions }}</p>
                        Tree numbers:
                        <div v-for="i in term.tree_numbers">
                          <span>{{ i }}</span>
                        </div>
                      </div>
                    </el-popover>
                  </div>
                </div>
              </div>
            </div>
          </div> -->
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios';
import { ElRow, ElCol, ElDescriptions, ElDescriptionsItem, ElPopover, ElTag, ElText } from 'element-plus';
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiInformationVariantCircleOutline, mdiMapMarker, mdiImageMarker, mdiCircleMedium } from '@mdi/js';
import { useSearchStore } from '../stores/store.js';
import { toRefs } from 'vue';

export default {
  setup() {
    const searchStore = useSearchStore();
    const state = toRefs(searchStore);
    return {
      ...state,
      handleSearch: searchStore.performSearch,
      splitAttributes: searchStore.splitAttributes,
      timestampToHumanDate: searchStore.timestampToHumanDate,
    };
  },
  components: {
    ElRow,
    ElCol,
    ElDescriptions,
    ElDescriptionsItem,
    ElPopover,
    SvgIcon,
    ElTag,
    ElText,

  },
  data() {
    return {
      accession: '',
      studyColDict: { 'bioproject': 'Bioproject', 'study_title': 'Study Title', 'study_abstract': 'Study Abstract' },
      mdiInfo_path: mdiInformationVariantCircleOutline,
      mdiMap_path: mdiMapMarker,
      mdiImageMap_path: mdiImageMarker,
      mdiCircle_path: mdiCircleMedium,
      meshTerm: [],
      meshTermTree: [],
      groupedMeshTerm: {},
    };
  },
  mounted() {
    console.log('Metadata template.');
    this.accession = this.$route.params.accession;
    const query = {
      'accession': this.accession,
      'contains_mesh_term': true,
    };
    this.handleSearch(query, 0);
  },
  watch: {
    searchResults: function (new_searchResults, old_searchResults) {
      console.log(`A searchResults returned! New query: ${new_searchResults[0]['mesh_indexing']}, Old query: ${old_searchResults[0]}`);
      this.getMeshTermById(new_searchResults[0]['mesh_indexing']);
    },
  },
  methods: {
    getMapUrl() {
      const apiKey = 'AIzaSyAGgq5zdgK24qKo50cbzAmQaTHzeCSqCn8';
      var url = ''
      if (this.searchResults[0]['latitude'] && this.searchResults[0]['longitude']) {
        url = `https://www.google.com/maps/embed/v1/place?key=${apiKey}&q=${this.searchResults[0]['latitude']},${this.searchResults[0]['longitude']}`;
      } else if (this.searchResults[0]['country']) {
        url = `https://www.google.com/maps/embed/v1/place?key=${apiKey}&q=${this.searchResults[0]['country']}`;
      } else if (this.searchResults[0]['inferred_country']) {
        url = `https://www.google.com/maps/embed/v1/place?key=${apiKey}&q=${this.searchResults[0]['inferred_country']}`;
      }
      console.log(url);
      return url;
    },
    getMeshTermById(mesh_ids) {
      const internalIP = window.location.hostname;
      const apiurl = `https://${internalIP}:5000/get_mesh_term_by_id`;
      const query = {
        'mesh_ids': mesh_ids
      }
      console.log(query);
      axios
        .post(apiurl, query)
        .then((response) => {
          this.meshTerm = response.data;
          // var temp_category_letter = [];
          for (let term of this.meshTerm) {
            term.tree_numbers = eval(term.tree_numbers);
            console.log(term.tree_numbers[0]);
            if (term.tree_numbers[0]) {
              term.category = term.tree_numbers[0][0];
            }
          }
          this.groupMeshTermByCategory();
          this.groupedMeshTerm = this.sortedGroupedMeshTerm();
        })
        .catch((error) => {
          console.error('An error occurred:', error);
        });
    },
    groupMeshTermByCategory() {
      for (const term of this.meshTerm) {
        const category = term.category;
        if (this.categoryDict.hasOwnProperty(category)) {
          const categoryLetter = category;
          if (!this.groupedMeshTerm.hasOwnProperty(categoryLetter)) {
            this.groupedMeshTerm[categoryLetter] = [];
          }
          this.groupedMeshTerm[categoryLetter].push(term);
        }
      }
    },
    sortedGroupedMeshTerm() {
      return Object.keys(this.groupedMeshTerm)
        .sort()
        .reduce((sortedObj, key) => {
          sortedObj[key] = this.groupedMeshTerm[key];
          return sortedObj;
        }, {});
    }

  }
}

</script>
