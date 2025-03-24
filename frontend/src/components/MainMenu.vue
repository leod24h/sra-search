<template>
  <div class="bg-black sticky top-0 shadow z-50 text-sm">
    <!-- Desktop Menu -->
    <div v-if="!isMobile" class="flex items-center justify-between px-8 py-2">
      <!-- Left Menu -->
      <div class="flex items-center">
        <!-- Uncomment if you want the logo back -->
        <a href="/">
          <img src="SRA-logo.png" alt="SRA Logo" class="w-8 h-8 mr-5" />
        </a>
        <ul class="flex space-x-4">
          <li>
            <a href="/" :class="{ 'text-white ': $route.path === '/', 'text-gray-300': $route.path !== '/' }"
              class="hover:text-gray-200">
              Home
            </a>
          </li>
          <li>
            <a href="/study"
              :class="{ 'text-white ': $route.path === '/study', 'text-gray-300': $route.path !== '/study' }"
              class="hover:text-gray-200">
              Search by Study
            </a>
          </li>
          <li>
            <a href="/sample"
              :class="{ 'text-white ': $route.path === '/sample', 'text-gray-300': $route.path !== '/sample' }"
              class="hover:text-gray-200">
              Search by Sample
            </a>
          </li>
          <li>
            <a href="/taxonomy"
              :class="{ 'text-white ': $route.path === '/taxonomy', 'text-gray-300': $route.path !== '/taxonomy' }"
              class="hover:text-gray-200">
              Taxonomy Browser
            </a>
          </li>
        </ul>
      </div>

      <!-- Right Menu (External Links) -->
      <ul class="flex space-x-4">
        <li>
          <a href="https://tracywong117.github.io/tracy-sra-doc/docs/intro/" target="_blank" rel="noopener noreferrer"
            class="text-gray-300 hover:text-gray-200">
            Docs
          </a>
        </li>
        <!-- <li>
          <a href="https://github.com/example/repo" target="_blank" rel="noopener noreferrer"
            class="text-gray-300 hover:text-gray-200">
            GitHub
          </a>
        </li> -->
      </ul>
    </div>

    <!-- Mobile Menu -->
    <div v-if="isMobile" class="border-b border-gray-700">
      <div class="flex items-center justify-between px-6 py-2" @click="isOpen = !isOpen">
        <img src="SRA-logo.png" alt="SRA Logo" class="w-8 h-8 mr-5" />
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"
          class="w-4 h-4 text-white cursor-pointer">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16m-7 6h7" />
        </svg>
      </div>
      <div v-if="isOpen" class="bg-gray-900">
        <!-- Main Navigation -->
        <ul class="grid grid-cols-2 gap-4 px-6 py-4">
          <li>
            <a href="/" class="block text-white hover:text-gray-200">Home</a>
          </li>
          <li>
            <a href="/study" class="block text-white hover:text-gray-200">Search by Study</a>
          </li>
          <li>
            <a href="/sample" class="block text-white hover:text-gray-200">Search by Sample</a>
          </li>
          <li>
            <a href="/taxonomy" class="block text-white hover:text-gray-200">Taxonomy Browser</a>
          </li>
          <!-- Empty li to balance the grid if needed -->
          <li class="hidden sm:block"></li>
        </ul>

        <!-- Divider -->
        <div class="border-t border-gray-700 mx-6"></div>

        <!-- External Links -->
        <ul class="grid grid-cols-2 gap-4 px-6 py-4">
          <li>
            <a href="https://docs.example.com" target="_blank" rel="noopener noreferrer"
              class="block text-white hover:text-gray-200">Docs</a>
          </li>

        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isOpen: false,
      isMobile: false,
    };
  },
  created() {
    this.checkScreenSize();
    window.addEventListener("resize", this.checkScreenSize);
  },
  destroyed() {
    window.removeEventListener("resize", this.checkScreenSize);
  },
  methods: {
    checkScreenSize() {
      this.isMobile = window.innerWidth <= 768;
    },
  },
};
</script>