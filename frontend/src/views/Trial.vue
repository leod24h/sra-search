<template>
  <div class="w-1/2 px-4 py-4">
    <!-- AG Grid Component -->
    <ag-grid-vue
      :domLayout="'autoHeight'"
      :rowData="rowData"
      :columnDefs="columnDefs"
      :defaultColDef="defaultColDef"
    ></ag-grid-vue>
  </div>
</template>

<script>
import { AgGridVue } from "ag-grid-vue3"; // Import AG Grid Vue component


export default {
  name: "CustomAgGrid",
  components: {
    AgGridVue,
  },
  data() {
    return {
      // Row data for the grid
      rowData: [
        { name: "John Doe", age: 25, country: "USA" },
        { name: "Jane Smith", age: 30, country: "Canada" },
        { name: "Sam Wilson", age: 22, country: "UK" },
      ],
      // Column definitions with customizations
      columnDefs: [
        {
          headerName: "Name",
          field: "name",
          cellStyle: { color: "blue", fontWeight: "bold" }, // Inline cell styles
        },
        {
          headerName: "Age",
          field: "age",
          cellRenderer: (params) => {
            // Custom cell renderer to highlight age
            return `<span style="color: ${
              params.value > 25 ? "red" : "green"
            }">${params.value} years</span>`;
          },
        },
        {
          headerName: "Country",
          field: "country",
          valueGetter: (params) => {
            // Custom value getter to format country name
            return `Country: ${params.data.country}`;
          },
        },
      ],
      // Default column definition
      defaultColDef: {
        sortable: true, // Enable sorting on all columns by default
        filter: true, // Enable filtering
        resizable: true, // Allow column resizing
      },
    };
  },
};
</script>