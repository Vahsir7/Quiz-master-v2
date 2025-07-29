<template>
    <div class="dashboard-header">
      <h2>My Quiz History</h2>
      <p>A record of all your past quiz attempts.</p>
      <button @click="handleExport" class="btn btn-primary mt-4">
        <i class="fas fa-file-csv"></i> Export to CSV
      </button>
    </div>

    <div v-if="exportMessage" class="success-box">{{ exportMessage }}</div>
    <div v-if="loading" class="text-center p-8">Loading history...</div>
    <div v-if="error" class="error-box">{{ error }}</div>

    <div v-if="!loading && !error" class="table-wrapper">
      <table class="data-table">
        <thead class="bg-gray-50">
          <tr>
            <th>Attempt ID</th>
            <th>Exam Name</th>
            <th>Score</th>
            <th>Total Marks</th>
            <th>Date Attempted</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="attempt in history" :key="attempt.attempt_id">
            <td>{{ attempt.attempt_id }}</td>
            <td class="font-medium">{{ attempt.exam_name }}</td>
            <td>
              <span class="font-semibold">{{ attempt.marks_obtained }}</span>
            </td>
            <td>{{ attempt.total_marks }}</td>
            <td>{{ new Date(attempt.attempt_date).toLocaleString() }}</td>
            <td>
              <router-link
                :to="{ name: 'StudentResults', params: { attemptId: attempt.attempt_id } }"
                class="btn-view-results"
              >
                View Results
              </router-link>
            </td>
          </tr>
          <tr v-if="history.length === 0">
            <td colspan="6" class="text-center text-gray-500 py-6">You have no quiz history yet.</td>
          </tr>
        </tbody>
      </table>
    </div>
</template>

<script>
import apiService from '@/services/apiService.js';
import StudentLayout from '@/components/StudentLayout.vue';

export default {
  name: 'StudentHistory',
  components: { StudentLayout },
  data() {
    return {
      history: [],
      loading: true,
      error: null,
      exportMessage: '',
    };
  },
  async mounted() {
    this.fetchHistory();
  },
  methods: {
    async fetchHistory() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiService.getStudentHistory();
        this.history = response.data;
      } catch (err) {
        this.error = 'Failed to load quiz history.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async handleExport() {
      this.exportMessage = '';
      this.error = null;
      try {
        const response = await apiService.exportStudentHistory();
        this.exportMessage = response.data.message;
      } catch (err) {
        this.error = 'Failed to start the export process.';
      }
    },
  },
}
</script>

<style scoped>
.table-wrapper {
  background-color: #ffffff;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  border-radius: 8px;
  overflow: hidden;
}
.btn-view-results {
  background-color: #3498db;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}
.btn-view-results:hover {
  background-color: #2980b9;
}
</style>
