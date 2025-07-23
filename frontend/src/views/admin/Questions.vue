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

      <div v-if="!loading && !error" class="space-y-6">
        <div v-if="questions.length === 0" class="text-center text-gray-500 py-8">
          No questions found for this exam. Click 'Add New Question' to begin.
        </div>
        
        <div v-for="(question, index) in questions" :key="question.QuestionID" class="bg-white shadow-lg rounded-lg overflow-hidden">
          <div class="p-4 bg-gray-50 border-b flex justify-between items-start">
            <p class="font-semibold text-gray-800 pr-4">
              {{ index + 1 }}. {{ question.QuestionStatement }}
            </p>
            <div class="space-x-3 flex-shrink-0">
              <button @click="openEditModal(question)" class="icon-edit" title="Edit Question"><i class="fas fa-pencil-alt"></i></button>
              <button @click="openDeleteModal(question)" class="icon-delete" title="Delete Question"><i class="fas fa-trash-alt"></i></button>
            </div>
          </div>

          <div class="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
            <div
              v-for="i in 4"
              :key="i"
              class="p-2 border rounded-md"
              :class="question.CorrectOption === i ? 'bg-green-100 border-green-400 text-green-800 font-semibold' : 'bg-gray-50'"
            >
              <span class="font-bold mr-2">{{ i }}:</span>
              <span>{{ question['Option' + i] }}</span>
              <i v-if="question.CorrectOption === i" class="fas fa-check-circle ml-2 text-green-600"></i>
            </div>
          </div>

          <div class="px-4 py-2 bg-gray-50 border-t text-xs text-gray-600 text-right">
              <span class="font-bold">Marks:</span> {{ question.Marks }}, 
              <span class="font-bold">Negative:</span> {{ question.NegMarks }}
          </div>
        </div>
      </div>

      <div v-if="isModalOpen" class="modal-overlay">
        <div class="modal-content max-w-2xl">
          <h3 class="text-xl font-semibold mb-4">{{ modal.isEditMode ? 'Edit Question' : 'Add New Question' }}</h3>
          <form @submit.prevent="handleFormSubmit" class="space-y-4">
            <div>
              <label class="block text-sm font-medium">Question Statement</label>
              <textarea v-model="modal.data.QuestionStatement" rows="3" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm"></textarea>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium">Option 1</label>
                <input type="text" v-model="modal.data.Option1" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
              </div>
              <div>
                <label class="block text-sm font-medium">Option 2</label>
                <input type="text" v-model="modal.data.Option2" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
              </div>
              <div>
                <label class="block text-sm font-medium">Option 3</label>
                <input type="text" v-model="modal.data.Option3" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
              </div>
              <div>
                <label class="block text-sm font-medium">Option 4</label>
                <input type="text" v-model="modal.data.Option4" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium">Correct Option</label>
                <select v-model="modal.data.CorrectOption" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
                  <option :value="1">Option 1</option>
                  <option :value="2">Option 2</option>
                  <option :value="3">Option 3</option>
                  <option :value="4">Option 4</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium">Marks</label>
                <input type="number" v-model="modal.data.Marks" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
              </div>
              <div>
                <label class="block text-sm font-medium">Negative Marks</label>
                <input type="number" v-model="modal.data.NegMarks" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
              </div>
            </div>
            <div class="flex justify-end space-x-4 pt-4">
              <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" class="btn btn-primary">Save Question</button>
            </div>
          </form>
        </div>
      </div>

      <div v-if="isDeleteModalOpen" class="modal-overlay">
          <div class="modal-content text-center">
              <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                  <i class="fas fa-exclamation-triangle text-red-600 text-xl"></i>
              </div>
              <h3 class="text-lg font-medium text-gray-900 mt-5">Are you sure?</h3>
              <p class="text-sm text-gray-500 mt-2">Do you really want to delete this question?</p>
              <div class="flex justify-center space-x-4 mt-6">
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
        this.error = "Failed to save question.";
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