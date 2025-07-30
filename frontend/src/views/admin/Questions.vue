<template>
  <div>
    <header class="content-header">
      <h2 class="content-header__title">Manage Questions</h2>
      <div class="header-actions">
        <button @click="openAddModal" class="btn btn-primary">
          <i class="fas fa-plus mr-2"></i> Add New Question
        </button>
      </div>
    </header>

    <main class="content-main">
      <div class="mb-4 p-4 border rounded-lg bg-gray-50">
        <h2 class="text-lg font-bold text-gray-800">Exam: {{ $route.query.examName || '...' }}</h2>
        <p class="text-md text-gray-700 mt-1">Subject: {{ $route.query.subjectName || '...' }}</p>
        <p class="text-md text-gray-700 mt-1">Chapter: {{ $route.query.chapterName || '...' }}</p>
      </div>

      <div v-if="loading" class="text-center">Loading questions...</div>
      <div v-if="error" class="text-center text-red-500 p-4 bg-red-100 rounded-md">{{ error }}</div>

      <div v-if="!loading && !error" class="questions-list">
        <div v-if="questions.length === 0" class="no-questions-card">
          No questions found for this exam. Click 'Add New Question' to begin.
        </div>

        <div v-for="(question, index) in questions" :key="question.QuestionID" class="question-card">
          <div class="question-header">
            <p class="question-statement">
              {{ index + 1 }}. {{ question.QuestionStatement }}
            </p>
            <div class="question-actions">
              <button @click="openEditModal(question)" class="icon-edit" title="Edit Question"><i class="fas fa-pencil-alt"></i></button>
              <button @click="openDeleteModal(question)" class="icon-delete" title="Delete Question"><i class="fas fa-trash-alt"></i></button>
            </div>
          </div>

          <div class="options-grid">
            <div
              v-for="i in 4"
              :key="i"
              class="option-item"
              :class="{ 'is-correct': question.CorrectOption === i }"
            >
              <span>{{ i }}: {{ question['Option' + i] }}</span>
              <i v-if="question.CorrectOption === i" class="fas fa-check-circle correct-icon"></i>
            </div>
          </div>

          <div class="question-footer">
              <strong>Marks:</strong> {{ question.Marks }},
              <strong>Negative:</strong> {{ question.NegMarks }}
          </div>
        </div>
      </div>

      <div v-if="isModalOpen" class="modal-overlay">
        <div class="modal-content max-w-2xl">
          <div class="modal-header">
            {{ modal.isEditMode ? 'Edit Question' : 'Add New Question' }}
          </div>
          <form @submit.prevent="handleFormSubmit">
            <div class="modal-body">
              <div class="form-group">
                <label>Question Statement</label>
                <textarea v-model="modal.data.QuestionStatement" rows="3" class="form-textarea"></textarea>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="form-group">
                  <label>Option 1</label>
                  <input type="text" v-model="modal.data.Option1" class="form-input">
                </div>
                <div class="form-group">
                  <label>Option 2</label>
                  <input type="text" v-model="modal.data.Option2" class="form-input">
                </div>
                <div class="form-group">
                  <label>Option 3</label>
                  <input type="text" v-model="modal.data.Option3" class="form-input">
                </div>
                <div class="form-group">
                  <label>Option 4</label>
                  <input type="text" v-model="modal.data.Option4" class="form-input">
                </div>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div class="form-group">
                  <label>Correct Option</label>
                  <select v-model="modal.data.CorrectOption" class="form-select">
                    <option :value="1">Option 1</option>
                    <option :value="2">Option 2</option>
                    <option :value="3">Option 3</option>
                    <option :value="4">Option 4</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Marks</label>
                  <input type="number" v-model="modal.data.Marks" class="form-input">
                </div>
                <div class="form-group">
                  <label>Negative Marks</label>
                  <input type="number" v-model="modal.data.NegMarks" class="form-input">
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" class="btn btn-primary">Save Question</button>
            </div>
          </form>
        </div>
      </div>

      <div v-if="isDeleteModalOpen" class="modal-overlay">
          <div class="modal-content text-center">
            <div class="modal-body">
              <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                  <i class="fas fa-exclamation-triangle text-red-600 text-xl"></i>
              </div>
              <h3 class="text-lg font-medium text-gray-900 mt-5">Are you sure?</h3>
              <p class="text-sm text-gray-500 mt-2">Do you really want to delete this question?</p>
            </div>
            <div class="modal-footer">
                <button @click="closeDeleteModal" class="btn btn-secondary">Cancel</button>
                <button @click="confirmDelete" class="btn btn-danger">Delete</button>
            </div>
          </div>
      </div>
    </main>
  </div>
</template>

<script>
import apiService from '@/services/apiService';

export default {
  name: 'QuestionsView',
  props: ['examId'],
  data() {
    return {
      loading: true,
      error: null,
      questions: [],
      isModalOpen: false,
      isDeleteModalOpen: false,
      modal: {
        isEditMode: false,
        data: {}
      },
      questionToDelete: null,
    };
  },
  async mounted() {
    this.fetchQuestions();
  },
  methods: {
    async fetchQuestions() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiService.getQuestions(this.examId);
        this.questions = response.data;
      } catch (err) {
        this.error = 'Failed to load questions.';
      } finally {
        this.loading = false;
      }
    },
    resetModal() {
      this.modal = {
        isEditMode: false,
        data: {
          QuestionStatement: '',
          Option1: '',
          Option2: '',
          Option3: '',
          Option4: '',
          CorrectOption: 1,
          Marks: 1,
          NegMarks: 0
        }
      };
    },
    openAddModal() {
      this.resetModal();
      this.isModalOpen = true;
    },
    openEditModal(question) {
      this.resetModal();
      this.modal.isEditMode = true;
      this.modal.data = { ...question };
      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
    },
    async handleFormSubmit() {
      const questionData = {
        ...this.modal.data,
        CorrectOption: parseInt(this.modal.data.CorrectOption),
        Marks: parseInt(this.modal.data.Marks),
        NegMarks: parseInt(this.modal.data.NegMarks)
      };

      try {
        if (this.modal.isEditMode) {
          await apiService.updateQuestion(this.modal.data.QuestionID, questionData);
        } else {
          await apiService.createQuestion(this.examId, questionData);
        }
        this.fetchQuestions();
        this.closeModal();
      } catch (err) {
        if (err.response && err.response.data && err.response.data.message) {
            this.error = err.response.data.message;
        } else {
            this.error = "Failed to save question.";
        }
      }
    },
    openDeleteModal(question) {
        this.questionToDelete = question;
        this.isDeleteModalOpen = true;
    },
    closeDeleteModal() {
        this.isDeleteModalOpen = false;
        this.questionToDelete = null;
    },
    async confirmDelete() {
        if (!this.questionToDelete) return;
        try {
            await apiService.deleteQuestion(this.questionToDelete.QuestionID);
            this.fetchQuestions();
            this.closeDeleteModal();
        } catch (err) {
            this.error = 'Failed to delete question.';
        }
    }
  }
};
</script>

<style scoped>
.questions-list {
  display: grid;
  gap: 1.5rem;
}
.no-questions-card {
  text-align: center;
  padding: 2rem;
  background-color: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  color: #6b7280;
}
.question-card {
  background-color: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  overflow: hidden;
}
.question-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 1.5rem;
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}
.question-statement {
  font-weight: 600;
  color: #1f2937;
  padding-right: 1rem;
}
.question-actions {
  display: flex;
  gap: 1rem;
  flex-shrink: 0;
}
.options-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 0.75rem;
  padding: 1.5rem;
}
@media (min-width: 768px) {
  .options-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
.option-item {
  padding: 0.75rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  background-color: #f9fafb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.option-item.is-correct {
  background-color: #dcfce7;
  border-color: #4ade80;
  color: #166534;
  font-weight: 500;
}
.correct-icon {
  color: #22c55e;
}
.question-footer {
  padding: 0.75rem 1.5rem;
  background-color: #f9fafb;
  border-top: 1px solid #e5e7eb;
  text-align: right;
  font-size: 0.875rem;
  color: #6b7280;
}
</style>
