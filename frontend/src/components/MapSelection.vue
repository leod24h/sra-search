<template>
  <div id="mapSelectRegion_plot" class="map-visualization"></div>
  <el-dialog v-model="dialogVisible" title="Searching" width="300px" style="border-radius: 10px;">
    Location <el-tag class="region-select-tab" color="rgb(237, 244, 247)"> {{ locationSelect }} </el-tag>
    <br> Total records: {{ locationCount }}
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button @click="handleLocationSelectSearch()" plain color="rgb(126, 175, 205)">
          Search
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import axios from 'axios';
import { ElDialog, ElButton, ElTag } from 'element-plus';
import Plotly from 'plotly.js-dist';
export default {
  components: {
    ElDialog,
    ElButton,
    ElTag,
  },
  data() {
    return {
      regionDataRows: [],
      dialogVisible: false,
      locationSelect: '',
      locationCount: 0,
    }
  },
  mounted() {
    this.loadRegionData();
  },
  methods: {
    loadRegionData() {
      const internalIP = window.location.hostname;
      console.log(internalIP);
      const url = `http://${internalIP}:5000/get_world_popularity`;
      console.log(url);
      axios.get(url)
        .then(response => {
          this.regionDataRows = response.data;
          this.mapSelectRegionVisualization();
        })
        .catch(error => {
          console.log(error);
        });
    },
    mapSelectRegionVisualization() {
      console.log()
      const data = [{
        type: 'choropleth',
        locationmode: 'country names',
        locations: this.regionDataRows.map(row => row.geo_loc_name_country_calc),
        z: this.regionDataRows.map(row => row.count_entity),
        hoverinfo: "location+z",
        // text: this.regionDataRows.map(row => row.geo_loc_name_country_calc),
        colorscale: [
          [0, 'rgb(242, 240, 247)'],     // Very light purple
          // [0.025, 'rgb(221, 214, 234)'], // Light purple
          // [0.05, 'rgb(200, 189, 221)'],  // Pale purple
          [0.25, 'rgb(179, 165, 209)'], // Lighter purple
          // [0.1, 'rgb(158, 141, 196)'],   // Medium-light purple
          // [0.15, 'rgb(137, 117, 183)'],  // Medium purple
          // [0.2, 'rgb(116, 93, 170)'],    // Medium-dark purple
          // [0.3, 'rgb(95, 69, 157)'],     // Dark purple
          [0.5, 'rgb(74, 45, 144)'],     // Darker purple
          // [0.6, 'rgb(54, 24, 131)'],     // Deep purple
          // [0.8, 'rgb(37, 10, 118)'],     // Deeper purple
          [1, 'rgb(24, 0, 105)']         // Very deep purple
        ],
        hoverlabel: {
          bgcolor: 'rgb(255,198,255)',

        },
        colorbar: {
          thickness: 5,
          len: 0.5,
          ticklabeloverflow: 'hide past div'
        },
        marker: {
          line: {
            width: 1
          }
        },
        seleted: {
          marker: {
            opacity: 0.7,
            color: 'rgb(208, 10, 136)'
          }
        }
      }];

      const layout = {
        geo: {
          scope: 'world',
          showland: true,

          landcolor: 'rgb(244,233,244)',
        },
        autosize: true,
        margin: {
          autoexpand: true,
          b: 0,
          l: 0,
          r: 0,
          t: 0,
        }
      };

      Plotly.newPlot('mapSelectRegion_plot', data, layout, { showLink: false, responsive: true, })
        .then(gd => {
          gd.on('plotly_click', eventData => {
            const clickedPoint = eventData.points[0];
            console.log(clickedPoint);

            this.locationSelect = clickedPoint.location;
            this.locationCount = clickedPoint.z;
            this.dialogVisible = true;

          });
          gd.on('plotly_hover', eventData => {
            const hoveredPoint = eventData.points[0];
            const hoveredPointNumber = eventData.points[0].pointNumber;
            var marker_width = [];
            var marker_color = [];
            for (var i = 0; i < hoveredPoint.data.z.length; i++) {
              marker_width[i] = 1
              marker_color[i] = '#444'
            };
            marker_width[hoveredPointNumber] = 2;
            marker_color[hoveredPointNumber] = '#DDC9FF'
            var update = {
              marker: {
                line: {
                  width: marker_width,
                  color: marker_color
                }
              }
            };
            Plotly.restyle('mapSelectRegion_plot', update, 0);

          });
        });
    },
    handleLocationSelectSearch() {
      this.dialogVisible = false;
    
      this.input_query = "";
      this.input_filters = [{
        operator: "AND",
        field: "geo",
        value: this.locationSelect,
        additional: "",
      }];
      this.input_filters = JSON.stringify(this.input_filters);
      console.log(this.input_filters);

      this.$router.push({
        path: '/sample_result',
        query: { search: this.input_query, filters: this.input_filters },
      });
    },
  }
}

</script>

<style></style>