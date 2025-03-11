<template>
  <el-popover placement="top" trigger="hover" width="25vw" @show="getOrganismInfo(organism)">
    <template #reference>
      <svg-icon type="mdi" :path="mdiInfo_path"
        class="pl-1 h-4 w-4 transition-transform duration-100 ease-in-out shrink-0 hover:scale-125"></svg-icon>
    </template>
    <div v-html="generateHTMLContent(organism)" style="display: flex; flex-direction: column;"></div>
  </el-popover>
</template>

<script>
import { ElPopover } from 'element-plus';
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiInformationVariantCircleOutline } from '@mdi/js';
import { useOrganismStore } from '../stores/organismWiki.js';
import { toRefs, onMounted } from 'vue';

export default {
  setup() {
    const organismStore = useOrganismStore();
    const state = toRefs(organismStore);
    onMounted(() => {
      organismStore.loadCacheFromLocalStorage();
    });
    return {
      ...state,
      setCacheInLocalStorage: organismStore.setCacheInLocalStorage,
      getOrganismInfo: organismStore.getOrganismInfo,
      generateHTMLContent: organismStore.generateHTMLContent,
    };
  },
  components: {
    ElPopover,
    SvgIcon,
  },
  data() {
    return {
      mdiInfo_path: mdiInformationVariantCircleOutline,
    };
  },
  props: {
    organism: String,
  },
}

</script>

<style>
.popup-card-image {
  align-self: center;
  max-width: 100%;
  height: 200px;
  margin: 10px 0;
}

</style>