<template>
  <el-input value="value" @input="e => $emit('input', e)"></el-input>
</template>
  
<script>
import { ElInput } from 'element-plus';

export default {
  components: {
    ElInput,
  },
  props: {
    value: String
  },
}
</script>
  
  
  