<template>
  <StudentLayout>
    <div v-if="loading" class="text-center">Loading Quiz...</div>
    <div v-if="error" class="error-box">{{ error }}</div>

    <div v-if="!loading && examDetails" class="quiz-container">
      <div class="quiz-header">
        <h2>{{ examDetails.exam_name }}</h2>
        <div class="timer">
          <i class="fas fa-clock"></i> Time Left: <span>{{ formattedTime }}</span>
        </div>
      </div>

      <div class="progress-bar">
        <div class="progress" :style="{ width: progressPercentage + '%' }"></div>
      </div>
      <p class="progress-text">Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}</p>

      <div class="question-card">
        <div class="question-header-container">
          <p class="question-statement">{{ currentQuestion.QuestionStatement }}</p>
          <div class="question-meta">
            <span class="marks">Marks: {{ currentQuestion.Marks }}</span>
            <span class="neg-marks">Negative: {{ currentQuestion.NegMarks }}</span>
          </div>
        </div>
        <div class="options-grid">
          <div
            v-for="i in 4"
            :key="i"
            class="option"
            :class="{ 'selected': answers[currentQuestion.QuestionID] === i }"
            @click="selectAnswer(currentQuestion.QuestionID, i)"
          >
            <span class="option-label">{{ i }}.</span>
            <span>{{ currentQuestion['Option' + i] }}</span>
          </div>
        </div>
      </div>

      <div class="quiz-navigation">
        <button @click="prevQuestion" :disabled="currentQuestionIndex === 0" class="btn-nav">Previous</button>
        <button v-if="currentQuestionIndex < questions.length - 1" @click="nextQuestion" class="btn-nav">Next</button>
        <button v-if="currentQuestionIndex < questions.length - 1" @click="submitQuiz" class="btn-submit">Finish</button>
        <button v-else @click="submitQuiz" class="btn-submit">Submit Quiz</button>
      </div>
    </div>
  </StudentLayout>
</template>

<script>
import apiService from '@/services/apiService';
import StudentLayout from '@/components/StudentLayout.vue';

export default {
  name: 'QuizView',
  components: { StudentLayout },
  props: ['examId'],
  data() {
    return {
      loading: true,
      error: null,
      attemptId: null,
      examDetails: null,
      questions: [],
      answers: {}, // { questionId: selectedOption }
      currentQuestionIndex: 0,
      timer: null,
      timeLeft: 0,
    };
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentQuestionIndex];
    },
    progressPercentage() {
      return ((this.currentQuestionIndex + 1) / this.questions.length) * 100;
    },
    formattedTime() {
      const minutes = Math.floor(this.timeLeft / 60);
      const seconds = this.timeLeft % 60;
      return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
  },
  async mounted() {
    this.startQuiz();
  },
  beforeUnmount() {
    clearInterval(this.timer);
  },
  methods: {
    async startQuiz() {
      try {
        const response = await apiService.startExam(this.examId);
        this.attemptId = response.data.attempt_id;
        this.examDetails = response.data.exam_details;
        this.questions = response.data.questions;
        this.timeLeft = this.examDetails.total_duration * 60;
        this.startTimer();
      } catch (err) {
        this.error = 'Failed to start the quiz.';
      } finally {
        this.loading = false;
      }
    },
    startTimer() {
      this.timer = setInterval(() => {
        if (this.timeLeft > 0) {
          this.timeLeft--;
        } else {
          clearInterval(this.timer);
          this.submitQuiz();
        }
      }, 1000);
    },
    selectAnswer(questionId, option) {
      this.answers[questionId] = option;
    },
    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++;
      }
    },
    prevQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--;
      }
    },
    async submitQuiz() {
      clearInterval(this.timer);
      this.loading = true;
      try {
        await apiService.submitExam(this.attemptId, this.answers);
        this.$router.push({ name: 'StudentResults', params: { attemptId: this.attemptId } });
      } catch (err) {
        this.error = 'Failed to submit your answers. Please try again.';
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.quiz-container { max-width: 800px; margin: auto; }
.quiz-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.timer { font-weight: bold; font-size: 1.2rem; color: #e74c3c; }
.progress-bar { height: 10px; background-color: #ecf0f1; border-radius: 5px; overflow: hidden; }
.progress { height: 100%; background-color: #3498db; transition: width 0.3s; }
.progress-text { text-align: right; font-size: 0.9rem; color: #7f8c8d; margin-top: 0.5rem; }
.question-card { background: white; padding: 2rem; border-radius: 8px; margin-top: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.question-header-container {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  gap: 1rem;
}
.question-statement { font-size: 1.25rem; font-weight: 500; flex-grow: 1; }
.question-meta {
  flex-shrink: 0;
  text-align: right;
  font-size: 0.9rem;
  color: #7f8c8d;
}
.marks {
  color: #27ae60;
  font-weight: bold;
  display: block;
}
.neg-marks {
  color: #c0392b;
  font-weight: bold;
  display: block;
}
.options-grid { display: grid; gap: 1rem; }
.option { padding: 1rem; border: 1px solid #bdc3c7; border-radius: 5px; cursor: pointer; transition: all 0.2s; }
.option:hover { background-color: #f9f9f9; }
.option.selected { border-color: #3498db; background-color: #eaf5fb; font-weight: bold; }
.option-label { font-weight: bold; margin-right: 0.5rem; }
.quiz-navigation { display: flex; justify-content: space-between; margin-top: 2rem; }
.btn-nav, .btn-submit { padding: 0.75rem 1.5rem; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; }
.btn-nav { background-color: #ecf0f1; }
.btn-nav:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-submit { background-color: #2ecc71; color: white; }
</style>
