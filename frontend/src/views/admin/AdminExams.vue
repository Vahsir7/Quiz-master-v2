<template>
  <div>
    <header class="content-header">
      <h2 class="content-header__title">Manage Exams</h2>
      <div class="header-actions">
        <button @click="openAddModal" class="btn btn-primary">
          <i class="fas fa-plus mr-2"></i> Add New Exam
        </button>
      </div>
    </header>

    <main class="content-main">
      <div v-if="loading" class="text-center">Loading exams...</div>
      <div v-if="error" class="error-box">{{ error }}</div>

      <div v-if="!loading" class="data-table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Exam Name</th>
              <th>Subject</th>
              <th>Chapter</th>
              <th>Questions</th>
              <th>Duration</th>
              <th>Exam Date</th>
              <th class="actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="exam in exams" :key="exam.ExamID">
              <td class="font-medium">{{ exam.ExamName }}</td>
              <td>{{ exam.SubjectName }}</td>
              <td>{{ exam.ChapterName }}</td>
              <td>{{ exam.TotalQuestions }}</td>
              <td>{{ exam.TotalDuration }} mins</td>
              <td>{{ new Date(exam.ExamDate).toLocaleDateString() }}</td>
              <td class="actions">
                <button @click="manageQuestions(exam)" class="icon-edit" title="Manage Questions">
                  <i class="fas fa-list-ul"></i>
                </button>
                <button @click="openEditModal(exam)" class="icon-edit" title="Edit Exam">
                  <i class="fas fa-pencil-alt"></i>
                </button>
                <button @click="openDeleteModal(exam)" class="icon-delete" title="Delete Exam">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </td>
            </tr>
            <tr v-if="exams.length === 0">
              <td colspan="7" class="text-center text-gray-500 py-4">No exams found.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="isModalOpen" class="modal-overlay">
        <div class="modal-content">
          <h3 class="text-xl font-semibold mb-4">{{ modal.isEditMode ? 'Edit Exam' : 'Add New Exam' }}</h3>
          <form @submit.prevent="handleFormSubmit" class="space-y-4">
            <template v-if="!modal.isEditMode">
              <div>
                <label class="block text-sm font-medium">Subject</label>
                <select v-model="selectedSubject" @change="fetchChaptersForSubject" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
                  <option disabled value="">Please select one</option>
                  <option v-for="subject in subjects" :key="subject.SubjectID" :value="subject.SubjectID">
                    {{ subject.SubjectName }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium">Chapter</label>
                <select v-model="modal.data.ChapterID" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" :disabled="!selectedSubject">
                  <option disabled value="">Please select one</option>
                  <option v-for="chapter in chapters" :key="chapter.ChapterID" :value="chapter.ChapterID">
                    {{ chapter.ChapterName }}
                  </option>
                </select>
              </div>
            </template>

            <div>
              <label class="block text-sm font-medium">Exam Name</label>
              <input type="text" v-model="modal.data.ExamName" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
            </div>
            <div>
              <label class="block text-sm font-medium">Total Duration (in minutes)</label>
              <input type="number" v-model="modal.data.TotalDuration" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
            </div>
            <div>
              <label class="block text-sm font-medium">Exam Date</label>
              <input type="date" v-model="modal.data.ExamDate" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
            </div>
            <div class="flex justify-end space-x-4 pt-4">
              <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" class="btn btn-primary">Save Exam</button>
            </div>
          </form>
        </div>
      </div>

      <div v-if="isDeleteModalOpen" class="modal-overlay">
        <div class="modal-content text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <i class="fas fa-exclamation-triangle text-red-600 text-xl"></i>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mt-5">Delete Exam</h3>
          <p class="text-sm text-gray-500 mt-2">Are you sure you want to delete the exam "{{ examToDelete.ExamName }}"?</p>
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
  name: 'AdminExamsView',
  data() {
    return {
      exams: [],
      subjects: [],
      chapters: [],
      selectedSubject: '',
      loading: true,
      error: null,
      isModalOpen: false,
      isDeleteModalOpen: false,
      modal: {
        isEditMode: false,
        data: {},
      },
      examToDelete: null,
    };
  },
  async mounted() {
    this.fetchExams();
    this.fetchSubjects();
  },
  methods: {
    async fetchExams() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiService.getExams();
        this.exams = response.data;
      } catch (err) {
        this.error = 'Failed to load exams.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async fetchSubjects() {
      try {
        const response = await apiService.getSubjects();
        this.subjects = response.data;
      } catch (err) {
        console.error('Failed to load subjects for modal.');
      }
    },
    async fetchChaptersForSubject() {
      if (!this.selectedSubject) {
        this.chapters = [];
        return;
      }
      try {
        const response = await apiService.getChapters(this.selectedSubject);
        this.chapters = response.data;
        // Reset chapter selection if the subject changes
        this.modal.data.ChapterID = '';
      } catch (err) {
        console.error('Failed to load chapters for selected subject.');
      }
    },
    resetModal() {
      this.modal = {
        isEditMode: false,
        data: {
          ExamName: '',
          TotalDuration: 60,
          ExamDate: new Date().toISOString().split('T')[0],
          ChapterID: '',
        },
      };
      this.selectedSubject = '';
      this.chapters = [];
    },
    openAddModal() {
      this.resetModal();
      this.isModalOpen = true;
    },
    openEditModal(exam) {
      this.resetModal();
      this.modal.isEditMode = true;
      this.modal.data = {
        ...exam,
        ExamDate: new Date(exam.ExamDate).toISOString().split('T')[0],
      };
      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
    },
    async handleFormSubmit() {
      try {
        if (this.modal.isEditMode) {
          await apiService.updateExam(this.modal.data.ExamID, this.modal.data);
        } else {
          if (!this.modal.data.ChapterID) {
            alert("Please select a chapter before creating an exam.");
            return;
          }
          await apiService.createExam(this.modal.data.ChapterID, this.modal.data);
        }
        this.fetchExams();
        this.closeModal();
      } catch (err) {
        this.error = `Failed to save exam.`;
        console.error(err);
      }
    },
    openDeleteModal(exam) {
      this.examToDelete = exam;
      this.isDeleteModalOpen = true;
    },
    closeDeleteModal() {
      this.isDeleteModalOpen = false;
      this.examToDelete = null;
    },
    async confirmDelete() {
      if (!this.examToDelete) return;
      try {
        await apiService.deleteExam(this.examToDelete.ExamID);
        this.fetchExams();
        this.closeDeleteModal();
      } catch (err) {
        this.error = 'Failed to delete exam.';
        console.error(err);
      }
    },
    manageQuestions(exam) {
      this.$router.push({
        name: 'Questions',
        params: { examId: exam.ExamID },
        query: {
            examName: exam.ExamName,
            subjectName: exam.SubjectName,
            chapterName: exam.ChapterName
        }
      });
    }
  },
};
</script>