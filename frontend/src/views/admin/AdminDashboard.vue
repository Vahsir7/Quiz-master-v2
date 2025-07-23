<template>
  <div class="dashboard-layout">
    <div class="main-content">
      <header class="content-header">
        <h2>Dashboard Overview</h2>
      </header>
      <main class="content-main">
        <div v-if="loading" class="loading-text">Loading dashboard data...</div>
        <div v-if="error" class="error-box">{{ error }}</div>
        
        <div v-if="!loading && !error">
          <div class="kpi-grid">
            <div class="kpi-card">
              <div class="icon-wrapper blue">
                <i class="fas fa-users"></i>
              </div>
              <div class="kpi-info">
                <h3>Total Students</h3>
                <p>{{ dashboardData.total_students }}</p>
              </div>
            </div>
            <div class="kpi-card">
              <div class="icon-wrapper green">
                <i class="fas fa-file-alt"></i>
              </div>
              <div class="kpi-info">
                <h3>Total Exams</h3>
                <p>{{ dashboardData.total_exams }}</p>
              </div>
            </div>
            <div class="kpi-card">
              <div class="icon-wrapper yellow">
                <i class="fas fa-check-circle"></i>
              </div>
              <div class="kpi-info">
                <h3>Total Attempts</h3>
                <p>{{ totalAttemptsCount }}</p>
              </div>
            </div>
            <div class="kpi-card">
              <div class="icon-wrapper purple">
                 <i class="fas fa-star-half-alt"></i>
              </div>
              <div class="kpi-info">
                <h3>Avg. Score</h3>
                <p>{{ averageScoreOverall.toFixed(2) }}%</p>
              </div>
            </div>
          </div>

          <div class="charts-grid">
            <div class="chart-card">
              <h3>Attempts per Subject</h3>
              <div class="chart-wrapper">
                <Bar v-if="chartData.attempts.labels.length" :data="chartData.attempts" :options="chartOptions" />
              </div>
            </div>
            <div class="chart-card">
              <h3>Average Score per Subject</h3>
               <div class="chart-wrapper">
                <Doughnut v-if="chartData.scores.labels.length" :data="chartData.scores" :options="chartOptions" />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
// (Your <script> section remains exactly the same)
import apiService from '@/services/apiService';
import { Bar, Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement } from 'chart.js';
import AdminNavbar from '@/components/AdminNavbar.vue';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement);

export default {
  name: 'AdminDashboard',
  components: { Bar, Doughnut, AdminNavbar },
  data() {
    return {
      loading: true,
      error: null,
      dashboardData: {
        total_students: 0,
        total_exams: 0,
        total_attempts: [],
        average_scores: [],
      },
      chartData: {
        attempts: { labels: [], datasets: [] },
        scores: { labels: [], datasets: [] },
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              color: '#6B7280'
            },
            grid: {
              color: '#E5E7EB'
            }
          },
          x: {
             ticks: {
              color: '#6B7280'
            },
            grid: {
              display: false
            }
          }
        }
      }
    };
  },
  computed: {
    totalAttemptsCount() {
        return this.dashboardData.total_attempts.reduce((sum, item) => sum + item.count, 0);
    },
    averageScoreOverall() {
        const totalScore = this.dashboardData.average_scores.reduce((sum, item) => sum + item.average_score, 0);
        return this.dashboardData.average_scores.length > 0 ? totalScore / this.dashboardData.average_scores.length : 0;
    }
  },
  async mounted() {
    try {
      const response = await apiService.getAdminDashboard();
      this.dashboardData = response.data;
      this.prepareChartData();
    } catch (err) {
      this.error = 'Failed to load dashboard data. Please ensure you are logged in and have a valid token.';
      console.error(err);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    prepareChartData() {
      this.chartData.attempts = {
        labels: this.dashboardData.total_attempts.map(item => item.subject),
        datasets: [{
          label: 'Total Attempts',
          backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'],
          borderColor: '#ffffff',
          borderWidth: 2,
          borderRadius: 5,
          data: this.dashboardData.total_attempts.map(item => item.count)
        }]
      };
      this.chartData.scores = {
        labels: this.dashboardData.average_scores.map(item => item.subject),
        datasets: [{
          label: 'Average Score',
          backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'],
          borderColor: '#ffffff',
          data: this.dashboardData.average_scores.map(item => item.average_score.toFixed(2))
        }]
      };
    },
    logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('userType');
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  height: 100vh;
  background-color: #f3f4f6; /* gray-100 */
}

.main-content {
  flex: 1; /* Take up remaining space */
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-header {
  background-color: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  padding: 1rem 1.5rem;
}

.content-header h2 {
  font-size: 1.5rem;
  font-weight: 600; /* semibold */
  color: #1f2937; /* gray-800 */
}

.content-main {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

/* Grids */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

/* Cards */
.kpi-card, .chart-card {
  background-color: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.kpi-card {
  display: flex;
  align-items: center;
}

.kpi-info h3 {
  font-size: 0.875rem;
  font-weight: 500; /* medium */
  color: #6b7280; /* gray-500 */
}

.kpi-info p {
  font-size: 1.5rem;
  font-weight: bold;
  color: #111827; /* gray-900 */
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 3rem;
  width: 3rem;
  border-radius: 9999px; /* rounded-full */
  color: white;
  margin-right: 1rem;
}
.icon-wrapper i {
  font-size: 1.25rem;
}

/* Icon Colors */
.icon-wrapper.blue { background-color: #3b82f6; }
.icon-wrapper.green { background-color: #10b981; }
.icon-wrapper.yellow { background-color: #f59e0b; }
.icon-wrapper.purple { background-color: #8b5cf6; }

/* Chart Styling */
.chart-card h3 {
  font-size: 1.125rem;
  font-weight: 500;
  margin-bottom: 1rem;
}
.chart-wrapper {
  height: 16rem; /* h-64 */
}

/* Responsive Grid Adjustments */
@media (max-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 640px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
}
</style>