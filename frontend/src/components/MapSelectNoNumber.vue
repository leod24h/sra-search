<template>
  <div id="mapSelectRegion_plot" class="map-visualization"></div>
  <div v-if="dialogVisible" @click="closeOnOutsideClick"
    class="fixed inset-0 bg-gray-600 text-gray-800 bg-opacity-50 flex items-center justify-center z-50">
    <div @click.stop class="bg-white p-4 rounded-lg w-64 shadow-lg relative">
      <button @click="dialogVisible = false"
        class="absolute top-1 right-1 text-gray-300 hover:text-gray-700 transition-colors">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
      <h3 class="text-base font-semibold mb-3">Searching</h3>
      <div class="mb-5 text-xs">
        Location: {{ locationSelect }}
        <br>
        Total records: {{ locationCount }}
      </div>
      <div class="flex justify-end space-x-2">
        <button @click="dialogVisible = false"
          class="px-3 py-1 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors text-xs">
          Cancel
        </button>
        <button @click="handleLocationSelectSearch()"
          class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors text-xs">
          Search
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Plotly from 'plotly.js-dist';

export default {
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
      const url = `http://${internalIP}:5000/get_world_popularity`;
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
        colorscale: [
          [0, 'rgb(242, 240, 247)'],     // Very light purple
          [1, 'rgb(242, 240, 247)']         // Very deep purple
        ],
        showscale: false,
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
      const searchQuery = {
        'place': this.locationSelect
      };
      this.$router.push({ name: 'View', query: { search: JSON.stringify(searchQuery) } });
    },
    closeOnOutsideClick(event) {
      if (event.target === event.currentTarget) {
        this.dialogVisible = false;
      }
    }
  }
}

</script>

<style scoped></style>