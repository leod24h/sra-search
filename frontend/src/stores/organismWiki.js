import { defineStore } from 'pinia';

export const useOrganismStore = defineStore('organism', {
  state: () => ({
    cache: {},
  }),
  actions: {
    // set the cache in local storage
    setCacheInLocalStorage() {
      localStorage.setItem('organismCache', JSON.stringify(this.cache));
    },
    // load the cache from local storage
    loadCacheFromLocalStorage() {
      const cache = localStorage.getItem('organismCache');
      if (cache) {
        this.cache = JSON.parse(cache);
      }
    },
    // clear the cache from local storage
    clearCacheFromLocalStorage() {
      localStorage.removeItem('organismCache');
    },
    getOrganismInfo(organism) {
      const regex = /\((.*?)\)/;
      const match = organism.match(regex);
      if (match && match.length > 1) {
        organism = match[1];
      }
      organism = organism.replace(/ metagenome$/, "");
      // console.log(organism);
      if (this.cache[organism]) {
        return true;
      } else {
        fetch(`https://en.wikipedia.org/w/api.php?action=opensearch&format=json&search=${organism}&origin=*`)
          .then(response => response.json())
          .then(data => {
            if (data[1].length == 0) {
              const pageInfo = {
                extract: "Not found.",
                thumbnail: ""
              };
              this.cache[organism] = pageInfo;
              this.setCacheInLocalStorage();
              return false;
            } else {
              const title = data[1][0];
              fetch(`https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts|pageimages&exintro=true&explaintext=true&piprop=thumbnail&pithumbsize=500&titles=${title}&redirects=true&origin=*`)
                .then(response => response.json())
                .then(data => {
                  const pageId = Object.keys(data.query.pages)[0];
                  console.log(data.query.pages[pageId]);
                  const extract = data?.query?.pages?.[pageId]?.extract ?? "Not found.";
                  const firstSentence = extract?.match(/^.+?[.!?]/)?.[0];
                  const thumbnail = data?.query?.pages?.[pageId]?.thumbnail;
                  const title = data?.query?.pages?.[pageId]?.title;
                  const pageInfo = {
                    extract: firstSentence,
                    thumbnail: thumbnail,
                    title: title,
                  };
                  this.cache[organism] = pageInfo;
                  this.setCacheInLocalStorage();
                  console.log(title);
                  return true;
                });
            }
          });
      }
    },
    generateHTMLContent(organism) {
      const regex = /\((.*?)\)/;
      const match = organism.match(regex);
      if (match && match.length > 1) {
        organism = match[1];
      }
      organism = organism.replace(/ metagenome$/, "");
      // console.log(organism);
      if (this.cache[organism]) {
        var thumbnail = this.cache[organism]?.thumbnail?.source ?? '';
        var extract = this.cache[organism]?.extract ?? 'Not found.';
        var title = this.cache[organism]?.title ?? '';
        if (thumbnail) {
          return `<div class="text-center bg-blue-50 text-gray-600"> ${title} </div>
            <img src="${thumbnail}" alt="Organism Thumbnail" class="popup-card-image" />` +
            `<div class="px-1 py-1">${extract}</span></div>
              <a href="https://en.wikipedia.org/wiki/${title}" class="text-right" target="_blank">Wikipedia</a>`;
        } else if (extract != 'Not found.') {
          return `<div class="text-center bg-blue-50 text-gray-600"> ${title} </div>
          <div class="px-1 py-1">${extract}</div><a href="https://en.wikipedia.org/wiki/${title}" class="text-right" target="_blank">Wikipedia</a>`;
        } else if (extract == 'Not found.') {
          return `<div>${extract}</div>`
        }

      }

      return '';
    },

  },

});