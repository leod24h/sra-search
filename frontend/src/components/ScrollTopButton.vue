<template>
  <el-backtop :bottom="100" :right="right">
    <div>
      <svg-icon type="mdi" :path="mdiBacktop_path" class="info-icon-popover" style="width: 30px; height: 30px;" />
    </div>
  </el-backtop>
</template>

<script>
import { ElBacktop } from 'element-plus';
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiArrowUpCircleOutline } from '@mdi/js';

export default {
  components: {
    ElBacktop,
    SvgIcon,
  },
  data() {
    return {
      mdiBacktop_path: mdiArrowUpCircleOutline,
    };
  },
  props: {
    right: {
      type: String,
      default: "100"
    }
  },
}

</script>

