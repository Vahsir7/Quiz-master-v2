<template>
  <StudentLayout>
    <div v-if="loading" class="text-center">Loading Results...</div>
    <div v-if="error" class="error-box">{{ error }}</div>

    <div v-if="!loading && results" class="results-container">
      <!-- Results Header -->
      <div class="results-header">
        <h2>Results for {{ results.exam_name }}</h2>
        <div class="score-summary">
          Your Score: <span>{{ results.score }} / {{ results.total_marks }}</span>
        </div>
      </div>

      <!-- Question Breakdown -->
      <div class="results-breakdown">
        <div v-for="(question, index) in results.results" :key="index" class="result-card">
          <p class="question-statement">{{ index + 1 }}. {{ question.QuestionStatement }}</p>
          <div class="options-grid">
            <div 
              v-for="i in 4" 
              :key="i" 
              class="option"
              :class="getOptionClass(question, i)"
            >
              {{ i }}. {{ question['Option' + i] }}
              <i v-if="question.CorrectOption === i" class="fas fa-check-circle"></i>
              <i v-if="question.YourAnswer === i && question.YourAnswer !== question.CorrectOption" class="fas fa-times-circle"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="text-center mt-8">
        <router-link to="/student/exams" class="btn-primary">Back to Exams</router-link>
      </div>
    </div>
  </StudentLayout>
</template>

<script>
import apiService from '@/services/apiService';
import StudentLayout from '@/components/StudentLayout.vue';

export default {
  name: 'ResultsView',
  components: { StudentLayout },
  props: ['attemptId'],
  data() {
    return {
      loading: true,
      error: null,
      results: null,
    };
  },
  async mounted() {
    this.fetchResults();
  },
  methods: {
    async fetchResults() {
      try {
        const response = await apiService.getExamResults(this.attemptId);
        this.results = response.data;
      } catch (err) {
        this.error = 'Failed to load results.';
      } finally {
        this.loading = false;
      }
    },
    getOptionClass(question, optionIndex) {
      const isCorrect = question.CorrectOption === optionIndex;
      const isSelected = question.YourAnswer === optionIndex;
      if (isCorrect) return 'correct';
      if (isSelected && !isCorrect) return 'incorrect';
      return '';
    }
  }
};
</script>

<style scoped>
.results-header { text-align: center; margin-bottom: 2rem; }
.score-summary { font-size: 1.5rem; margin-top: 0.5rem; }
.score-summary span { font-weight: bold; color: #2ecc71; }
.results-breakdown { display: grid; gap: 1.5rem; }
.result-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.question-statement { font-weight: 500; margin-bottom: 1rem; }
.options-grid { display: grid; gap: 0.5rem; }
.option { padding: 0.75rem; border-radius: 5px; border: 1px solid #ecf0f1; display: flex; justify-content: space-between; align-items: center; }
.option.correct { background-color: #e8f5e9; border-color: #a5d6a7; color: #2e7d32; font-weight: bold; }
.option.incorrect { background-color: #ffebee; border-color: #ef9a9a; color: #c62828; }
.btn-primary { background-color: #3498db; color: white; padding: 0.75rem 1.5rem; border-radius: 5px; text-decoration: none; font-weight: bold; }
</style>
