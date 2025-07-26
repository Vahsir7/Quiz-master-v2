<template>
  <StudentLayout>
    <div class="dashboard-header">
      <h2>Your Dashboard</h2>
      <p>An overview of your performance and activity.</p>
    </div>

    <div v-if="loading" class="text-center">Loading dashboard data...</div>
    <div v-if="error" class="error-box">{{ error }}</div>

    <div v-if="!loading && !error">
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
         <div class="stat-card">
          <i class="fas fa-trophy stat-icon orange"></i>
          <div class="stat-info">
            <h3>Highest Score</h3>
            <p>{{ stats.highest_score || 0 }}</p>
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
          <h3>Average Score per Subject (%)</h3>
          <div class="chart-wrapper">
            <Doughnut v-if="chartData.scores.labels.length" :data="chartData.scores" :options="chartOptions" />
          </div>
        </div>
        <div class="chart-card">
          <h3>Performance Over Time (Score/Total)</h3>
          <div class="chart-wrapper">
            <Line v-if="chartData.performance.labels.length" :data="chartData.performance" :options="chartOptions" />
          </div>
        </div>
      </div>
    </div>
  </StudentLayout>
</template>

<script>
import apiService from '@/services/apiService';
import StudentLayout from '@/components/StudentLayout.vue';
import { Bar, Doughnut, Line } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement, PointElement, LineElement } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement, PointElement, LineElement);

export default {
  name: 'StudentDashboard',
  components: { StudentLayout, Bar, Doughnut, Line },
  data() {
    return {
      stats: {
        total_attempts: [],
        average_scores: [],
        average_score: 0,
        total_exams: 0,
        highest_score: 0,
        attempts_over_time: [],
      },
      loading: true,
      error: null,
      chartData: {
        attempts: { labels: [], datasets: [] },
        scores: { labels: [], datasets: [] },
        performance: { labels: [], datasets: [] }
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
        this.prepareChartData();
      } catch (err) {
        this.error = 'Failed to load dashboard data.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    prepareChartData() {
      this.chartData.attempts = {
        labels: this.stats.total_attempts.map(item => item.subject),
        datasets: [{
          label: 'Total Attempts',
          backgroundColor: '#3498db',
          borderRadius: 4,
          data: this.stats.total_attempts.map(item => item.count)
        }]
      };

      this.chartData.scores = {
        labels: this.stats.average_scores.map(item => item.subject),
        datasets: [{
          label: 'Average Score',
          backgroundColor: ['#2ecc71', '#f1c40f', '#e74c3c', '#9b59b6', '#34495e'],
          data: this.stats.average_scores.map(item => item.average_score.toFixed(2))
        }]
      };
      
      this.chartData.performance = {
        labels: this.stats.attempts_over_time.map((_, index) => `Attempt ${index + 1}`),
        datasets: [{
          label: 'Score per Attempt',
          backgroundColor: '#ef4444',
          borderColor: '#ef4444',
          data: this.stats.attempts_over_time.map(item => item.score)
        }]
      };
    },
  },
};
</script>
