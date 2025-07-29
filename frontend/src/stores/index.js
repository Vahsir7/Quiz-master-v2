import { createStore } from 'vuex';
import apiService from '@/services/apiService';

export default createStore({
  // STATE: Data your components will use
  state: {
    // Original counter state
    count: 0,

    // New state for the quiz
    quiz: {
      loading: true,
      error: null,
      attemptId: null,
      examDetails: null,
      questions: [],
      answers: {},
      currentQuestionIndex: 0,
      timeLeft: 0,
    }
  },

  // GETTERS: Computed properties for your store
  getters: {
    // Original counter getter
    doubleCount: state => state.count * 2,

    // New getters for the quiz
    currentQuestion: state => state.quiz.questions[state.quiz.currentQuestionIndex],
    progressPercentage: state => ((state.quiz.currentQuestionIndex + 1) / state.quiz.questions.length) * 100,
    formattedTime: state => {
      const minutes = Math.floor(state.quiz.timeLeft / 60);
      const seconds = state.quiz.timeLeft % 60;
      return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
  },

  // MUTATIONS: Synchronous functions to change the state
  mutations: {
    // Original counter mutation
    increment(state) {
      state.count++;
    },

    // New mutations for the quiz
    setQuizLoading(state, isLoading) {
      state.quiz.loading = isLoading;
    },
    setQuizData(state, payload) {
      state.quiz.attemptId = payload.attempt_id;
      state.quiz.examDetails = payload.exam_details;
      state.quiz.questions = payload.questions;
      state.quiz.timeLeft = payload.exam_details.total_duration * 60;
      state.quiz.error = null;
    },
    setQuizError(state, error) {
      state.quiz.error = error;
    },
    selectAnswer(state, { questionId, option }) {
      state.quiz.answers[questionId] = option;
    },
    nextQuestion(state) {
      if (state.quiz.currentQuestionIndex < state.quiz.questions.length - 1) {
        state.quiz.currentQuestionIndex++;
      }
    },
    prevQuestion(state) {
      if (state.quiz.currentQuestionIndex > 0) {
        state.quiz.currentQuestionIndex--;
      }
    },
    decrementTime(state) {
      state.quiz.timeLeft--;
    },
    resetQuizState(state) {
      state.quiz = {
        loading: true,
        error: null,
        attemptId: null,
        examDetails: null,
        questions: [],
        answers: {},
        currentQuestionIndex: 0,
        timeLeft: 0,
      };
    }
  },

  // ACTIONS: Asynchronous functions that commit mutations
  actions: {
    // Original counter action
    increment(context) {
      context.commit('increment');
    },

    // New actions for the quiz
    async startQuiz({ commit }, examId) {
      commit('setQuizLoading', true);
      try {
        const response = await apiService.startExam(examId);
        commit('setQuizData', response.data);
      } catch (err) {
        commit('setQuizError', 'Failed to start the quiz.');
      } finally {
        commit('setQuizLoading', false);
      }
    },
    async submitQuiz({ state, commit }) {
      commit('setQuizLoading', true);
      try {
        await apiService.submitExam(state.quiz.attemptId, state.quiz.answers);
        return state.quiz.attemptId; // Return attemptId for routing
      } catch (err) {
        commit('setQuizError', 'Failed to submit your answers.');
        commit('setQuizLoading', false);
        throw err; // Re-throw to handle in component
      }
    },
  },
  modules: {}
});
