import { defineStore } from 'pinia';
import axios from 'axios';

export const useSearchStore = defineStore('search', {
  state: () => ({
    input_query: '', // search query
    input_filters: [], // filters for the search
    searchResults: [],
    searchResultsTotal: 0,
    searchResultsCount: 0,
    headers: [
      "acc",
      "experiment",
      "biosample",
      "organism",
      "bioproject",
      "sra_study",
      "releasedate",
      "collectiondate",
      "center_name",
      "country",
      "latitude",
      "longitude",
      "attributes",
      "instrument"
    ],
    categoryDict: {
      "A": "Anatomy",
      "B": "Organisms",
      "C": "Diseases",
      "D": "Chemicals and Drugs",
      "E": "Analytical, Diagnostic and Therapeutic Techniques, and Equipment",
      "F": "Psychiatry and Psychology",
      "G": "Phenomena and Processes",
      "H": "Disciplines and Occupations",
      "I": "Anthropology, Education, Sociology and Social Phenomena",
      "J": "Technology, Industry, and Agriculture",
      "K": "Humanities",
      "L": "Information Science",
      "M": "Names Groups",
      "N": "Health Care",
      "V": "Publication Characteristics",
      "Z": "Geographicals"
    },
    searchHistory: [], // only the text query

  }),
  actions: {
    performSearch(query, offset = 0) {
      const internalIP = window.location.hostname;
      const apiurl = `https://${internalIP}:5000/search`;

      query.offset = offset;

      axios
        .post(apiurl, query)
        .then((response) => {
          this.searchResults = response.data.data;
          this.searchResultsCount = response.data.count;
          this.searchResultsTotal = response.data.total;
        })
        .catch((error) => {
          console.error('An error occurred:', error);
        });
    },
    splitAttributes(text) {
      if (!text || text.trim().length === 0) {
        return [];
      }
      const lines = text.trim().split("\n");
      return lines.map((line) => {
        const [key, value] = line.trim().split(":");
        if (key) {
          const trimmedKey = key.trim();
          return {
            key: trimmedKey,
            value: value ? value.trim() : null,
          };
        }
        return null;
      }).filter((item) => item !== null);
    },
    timestampToHumanDate(timestamp) {
      var date = new Date(timestamp * 1000);
      var humanDate = date.toLocaleDateString();
      return humanDate;
    },
    addSearchHistory(query) {
      this.searchHistory.push(query);
      // limit to 10 searches history only
      if (this.searchHistory.length > 10) {
        this.searchHistory.shift();
      }
      console.log(this.searchHistory);

    },
    calculateDistance(lat1, lng1, lat2, lng2) {
      const earthRadius = 6371; // Radius of the Earth in kilometers

      // Convert latitude and longitude to radians
      const lat1Rad = this.degToRad(lat1);
      const lng1Rad = this.degToRad(lng1);
      const lat2Rad = this.degToRad(lat2);
      const lng2Rad = this.degToRad(lng2);

      // Calculate the differences between coordinates
      const latDiff = lat2Rad - lat1Rad;
      const lngDiff = lng2Rad - lng1Rad;

      // Calculate the distance using the Haversine formula
      const a =
        Math.sin(latDiff / 2) ** 2 +
        Math.cos(lat1Rad) * Math.cos(lat2Rad) * Math.sin(lngDiff / 2) ** 2;
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      const distance = earthRadius * c;

      return distance;
    },
    degToRad(degrees) {
      return degrees * (Math.PI / 180);
    },

  }
});