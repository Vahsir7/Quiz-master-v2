<template>
  <StudentLayout>
    <div class="dashboard-header">
      <h2>Your Dashboard</h2>
      <p>An overview of your performance and activity.</p>
    </div>

    <div v-if="loading" class="text-center">Loading dashboard data...</div>
    <div v-if="error" class="error-box">{{ error }}</div>

    <div v-if="!loading && !error">
      <!-- Statistics Grid -->
      <div class="stats-grid">
        <div class="stat-card">
          <i class="fas fa-file-alt stat-icon blue"></i>
          <div class="stat-info">
            <h3>Total Quizzes Taken</h3>
            <p>{{ stats.total_exams || 0 }}</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-check-circle stat-icon green"></i>
          <div class="stat-info">
            <h3>Total Attempts</h3>
            <p>{{ totalAttemptsCount }}</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-star-half-alt stat-icon yellow"></i>
          <div class="stat-info">
            <h3>Overall Average Score</h3>
            <p>{{ (stats.average_score || 0).toFixed(2) }}%</p>
          </div>
        </div>
      </div>

      <!-- FIX: Replaced the simple list with a grid for charts -->
      <div class="charts-grid">
        <div class="chart-card">
          <h3>Attempts per Subject</h3>
          <div class="chart-wrapper">
            <!-- Render the Bar chart if data is available -->
            <Bar v-if="chartData.attempts.labels.length" :data="chartData.attempts" :options="chartOptions" />
          </div>
        </div>
        <div class="chart-card">
          <h3>Average Score per Subject (%)</h3>
          <div class="chart-wrapper">
            <!-- Render the Doughnut chart if data is available -->
            <Doughnut v-if="chartData.scores.labels.length" :data="chartData.scores" :options="chartOptions" />
          </div>
        </div>
      </div>
    </div>
  </StudentLayout>
</template>

<script>
import apiService from '@/services/apiService';
import StudentLayout from '@/components/StudentLayout.vue';
// FIX: Import Chart.js components
import { Bar, Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement } from 'chart.js';

// FIX: Register Chart.js components
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement);

export default {
  name: 'StudentDashboard',
  // FIX: Add chart components
  components: { StudentLayout, Bar, Doughnut },
  data() {
    return {
      stats: {
        total_attempts: [],
        average_scores: [],
        average_score: 0,
        total_exams: 0,
      },
      loading: true,
      error: null,
      // FIX: Add data properties for charts
      chartData: {
        attempts: { labels: [], datasets: [] },
        scores: { labels: [], datasets: [] },
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
      },
    };
  },
  computed: {
    totalAttemptsCount() {
      return this.stats.total_attempts.reduce((sum, item) => sum + item.count, 0);
    }
  },
  async mounted() {
    this.fetchDashboardData();
  },
  methods: {
    async fetchDashboardData() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiService.getStudentDashboard();
        this.stats = response.data;
        // FIX: Call method to prepare chart data after fetching
        this.prepareChartData();
      } catch (err) {
        this.error = 'Failed to load dashboard data.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    // FIX: Add a new method to format API data for Chart.js
    prepareChartData() {
      // Data for Attempts Bar Chart
      this.chartData.attempts = {
        labels: this.stats.total_attempts.map(item => item.subject),
        datasets: [{
          label: 'Total Attempts',
          backgroundColor: '#3498db',
          borderRadius: 4,
          data: this.stats.total_attempts.map(item => item.count)
        }]
      };

      // Data for Scores Doughnut Chart
      this.chartData.scores = {
        labels: this.stats.average_scores.map(item => item.subject),
        datasets: [{
          label: 'Average Score',
          backgroundColor: ['#2ecc71', '#f1c40f', '#e74c3c', '#9b59b6', '#34495e'],
          data: this.stats.average_scores.map(item => item.average_score.toFixed(2))
        }]
      };
    },
  },
};
</script>

<style scoped>
.dashboard-header { margin-bottom: 2rem; }
.dashboard-header h2 { font-size: 2rem; font-weight: bold; color: #2c3e50; }
.dashboard-header p { font-size: 1rem; color: #7f8c8d; }
.error-box { background-color: #e74c3c; color: white; padding: 1rem; border-radius: 5px; margin: 1rem 0; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.stat-icon {
  font-size: 2rem;
  padding: 1rem;
  border-radius: 50%;
  color: white;
  margin-right: 1rem;
}
.stat-icon.blue { background-color: #3498db; }
.stat-icon.green { background-color: #2ecc71; }
.stat-icon.yellow { background-color: #f1c40f; }

.stat-info h3 {
  font-size: 0.9rem;
  color: #7f8c8d;
  font-weight: 500;
}
.stat-info p {
  font-size: 1.75rem;
  font-weight: bold;
  color: #2c3e50;
}

/* FIX: Added styles for the charts section */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.chart-card {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.chart-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #34495e;
  margin-bottom: 1rem;
}

.chart-wrapper {
  height: 300px;
  position: relative;
}
</style>
