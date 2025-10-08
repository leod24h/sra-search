<template>
  <div style="padding: 4vh 8vw 10vh 8vw;">
    <el-row :gutter="50">
      <el-col :xs="24" :sm="24" :md="18">
        <div v-if="searchResults[0]">
          <div class="text-custom-purple font-semibold text-lg"> {{ accession }} </div>
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
          <div class="font-bold text-lg text-gray-800"> Related Study</div>
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
      <!-- <el-col :xs="24" :sm="24" :md="6">
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
        </div>
      </el-col> -->
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
      studyColDict: { 'bioproject': 'Bioproject', 'sra_study': 'SRA Study', 'study_title': 'Study Title', 'study_abstract': 'Study Abstract' },
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
    this.fetchSample(this.accession);
    console.log(this.searchResults);
  },
  watch: {
    searchResults: function (new_searchResults, old_searchResults) {
      console.log(`A searchResults returned! New query: ${new_searchResults[0]['mesh_indexing']}, Old query: ${old_searchResults[0]}`);
      // this.getMeshTermById(new_searchResults[0]['mesh_indexing']);
    },
  },
  methods: {
    fetchSample(acc){
      const internalIP = window.location.hostname;
      const apiurl = `http://${internalIP}:5000/fetch_sample`;
      
      axios
      .get(apiurl, { params: { query: acc } })
      .then((response) => {
        this.headers.forEach((header, index) => {
          this.searchResults[header] = response.data[0][index];
        });
        this.searchResults = [this.searchResults];
        this.fetch_study(this.searchResults[0]['sra_study']);
      })
      .catch((error) => {
        console.error('An error occurred:', error);
      });
      
    },
    fetch_study(sra_study) {
      const internalIP = window.location.hostname;
      const apiurl = `http://${internalIP}:5000/fetch_study`;

      axios
        .get(apiurl, { params: { query: sra_study } })
        .then((response) => {
          this.searchResults[0]['study_title'] = response.data[0][0];
          this.searchResults[0]['study_abstract'] = response.data[0][1];
        })
        .catch((error) => {
          console.error('An error occurred:', error);
        });
    },
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
    
  }
}

</script>
