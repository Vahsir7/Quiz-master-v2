<template>
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
            @click="selectAnswer({ questionId: currentQuestion.QuestionID, option: i })"
          >
            <span class="option-label">{{ i }}.</span>
            <span>{{ currentQuestion['Option' + i] }}</span>
          </div>
        </div>
      </div>

      <div class="quiz-navigation">
        <button @click="prevQuestion" :disabled="currentQuestionIndex === 0" class="btn-nav">Previous</button>
        <button v-if="currentQuestionIndex < questions.length - 1" @click="nextQuestion" class="btn-nav">Next</button>
        <button v-if="currentQuestionIndex < questions.length - 1" @click="handleQuizSubmit" class="btn-submit">Finish</button>
        <button v-else @click="handleQuizSubmit" class="btn-submit">Submit Quiz</button>
      </div>
    </div>
</template>

<script>
import { mapState, mapGetters, mapActions, mapMutations } from 'vuex';
import StudentLayout from '@/components/StudentLayout.vue';

export default {
  name: 'QuizView',
  components: { StudentLayout },
  props: ['examId'],
  data() {
    return {
      timerInterval: null,
    };
  },
  computed: {
    ...mapState({
      loading: state => state.quiz.loading,
      error: state => state.quiz.error,
      examDetails: state => state.quiz.examDetails,
      questions: state => state.quiz.questions,
      answers: state => state.quiz.answers,
      currentQuestionIndex: state => state.quiz.currentQuestionIndex,
    }),
    ...mapGetters([
      'currentQuestion',
      'progressPercentage',
      'formattedTime'
    ]),
  },
  methods: {
    ...mapActions([
      'startQuiz',
      'submitQuiz'
    ]),
    ...mapMutations([
      'selectAnswer',
      'nextQuestion',
      'prevQuestion',
      'decrementTime',
      'resetQuizState',
    ]),

    startTimer() {
      this.timerInterval = setInterval(() => {
        if (this.$store.state.quiz.timeLeft > 0) {
          this.decrementTime();
        } else {
          clearInterval(this.timerInterval);
          this.handleQuizSubmit();
        }
      }, 1000);
    },

    async handleQuizSubmit() {
      clearInterval(this.timerInterval);
      try {
        const attemptId = await this.submitQuiz();
        this.$router.push({ name: 'StudentResults', params: { attemptId } });
      } catch (err) {
        this.error = 'Failed to submit quiz. Please try again.';
      }
    }
  },
  async mounted() {
    this.resetQuizState();
    await this.startQuiz(this.examId);
    if (!this.error) {
      this.startTimer();
    }
  },
  beforeUnmount() {
    clearInterval(this.timerInterval);
  },
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
.question-header-container { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; gap: 1rem; }
.question-statement { font-size: 1.25rem; font-weight: 500; flex-grow: 1; }
.question-meta { flex-shrink: 0; text-align: right; font-size: 0.9rem; color: #7f8c8d; }
.marks { color: #27ae60; font-weight: bold; display: block; }
.neg-marks { color: #c0392b; font-weight: bold; display: block; }
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
