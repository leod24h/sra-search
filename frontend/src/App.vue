<template>
  <div id="app">
    <main-menu></main-menu>
    <router-view class="min-h-screen"/>
    <app-footer></app-footer>
  </div>
</template>

<script>
import MainMenu from './components/MainMenu.vue';
import AppHeader from './components/AppHeader.vue';
import AppFooter from './components/AppFooter.vue';

export default {
  components: {
    MainMenu,
    AppHeader,
    AppFooter,
  },

}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Playfair&display=swap');
@import './assets/css/loading-animation.css';
@import './assets/css/color.css';

body {
  /* font-family: Poppins, Playfair, Switzer, Inter, DM Sans, Mona Sans, Arial, sans-serif; */
  font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "Liberation Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
  margin: 0px;
  overflow-x: hidden;
}

html {
  font-size: 22px;
}

@media (min-width: 2160px) {
  html {
    font-size: 30px;
  }
}

.el-popover.el-popper {
  word-break: break-word;
  text-align: left;
}


.attribute-tag {
  font-size: 0.7rem;
  border-radius: 1rem;
  border-color: var(--pink-light-1);
  background-color: var(--pink-light-1);
  color: var(--pink-1);
  margin-top: 0.1rem;
  margin-bottom: 0.1rem;
  margin-left: -0.3rem;
}




</style>