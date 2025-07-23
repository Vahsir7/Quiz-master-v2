<template>
  <AdminLayout>
    <template #header-title>
      Manage Exams
    </template>
    <template #header-actions>
      <button @click="openAddModal" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-lg flex items-center">
        <i class="fas fa-plus mr-2"></i> Add New Exam
      </button>
    </template>

    <div v-if="chapterId" class="mb-4 p-4 border rounded-lg bg-gray-50">
      <h2 class="text-lg font-bold text-gray-800">Showing exams for Chapter:</h2>
      <p class="text-md text-gray-700 mt-1">{{ $route.query.chapterName || '...' }}</p>
    </div>

    <div v-if="!loading && !error" class="bg-white shadow-lg rounded-lg overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Exam Name</th>
            <th v-if="!chapterId" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Subject & Chapter</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Questions</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="exam in exams" :key="exam.ExamID">
            <td class="px-6 py-4 font-medium">{{ exam.ExamName }}</td>
            <td v-if="!chapterId" class="px-6 py-4 text-sm text-gray-500">
              <div>{{ exam.SubjectName }}</div>
              <div>{{ exam.ChapterName }}</div>
            </td>
            <td class="px-6 py-4">{{ exam.TotalQuestions }}</td>
            <td class="px-6 py-4">{{ new Date(exam.ExamDate).toLocaleDateString() }}</td>
            <td class="px-6 py-4 text-right space-x-4">
              <button @click="viewQuestions(exam)" class="text-green-600 hover:text-green-800" title="View/Add Questions"><i class="fas fa-eye"></i></button>
              <button @click="openEditModal(exam)" class="text-indigo-600 hover:text-indigo-800" title="Edit Exam"><i class="fas fa-pencil-alt"></i></button>
              <button @click="openDeleteModal(exam)" class="text-red-600 hover:text-red-800" title="Delete Exam"><i class="fas fa-trash-alt"></i></button>
            </td>
          </tr>
          <tr v-if="exams.length === 0">
            <td :colspan="chapterId ? 4 : 5" class="px-6 py-4 text-center text-gray-500">No exams found.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="loading" class="text-center mt-4">Loading exams...</div>
    <div v-if="error" class="text-center text-red-500 p-4 bg-red-100 rounded-md mt-4">{{ error }}</div>

    <div v-if="isModalOpen" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ modal.isEditMode ? 'Edit Exam' : 'Create New Exam' }}</h3>
        <form @submit.prevent="handleFormSubmit" class="mt-4">
          
          <fieldset v-if="!modal.isEditMode">
            <div class="mb-4">
              <label for="subject" class="block text-sm font-medium text-gray-700">Subject</label>
              <div class="flex items-center space-x-2 mt-1">
                <select id="subject" v-model="modal.selectedSubjectId" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" :disabled="modal.subjectConfirmed">
                  <option disabled value="">Please select a subject</option>
                  <option v-for="subj in subjects" :key="subj.SubjectID" :value="subj.SubjectID">{{ subj.SubjectName }}</option>
                </select>
                <button type="button" @click="confirmSubject" v-if="!modal.subjectConfirmed" :disabled="!modal.selectedSubjectId" class="btn btn-primary flex-shrink-0">Confirm</button>
                <button type="button" @click="changeSubject" v-else class="btn btn-secondary flex-shrink-0">Change</button>
              </div>
            </div>
            <div class="mb-4" v-if="modal.subjectConfirmed">
              <label for="chapter" class="block text-sm font-medium text-gray-700">Chapter</label>
              <select id="chapter" v-model="modal.data.ChapterID" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
                <option disabled value="">Please select a chapter</option>
                <option v-for="chap in chapters" :key="chap.ChapterID" :value="chap.ChapterID">{{ chap.ChapterName }}</option>
              </select>
            </div>
          </fieldset>

          <fieldset :disabled="!modal.data.ChapterID && !modal.isEditMode">
            <div class="grid grid-cols-1 gap-6 mt-4 border-t pt-4">
              <div>
                <label for="examName" class="block text-sm font-medium text-gray-700">Exam Name</label>
                <input type="text" v-model="modal.data.ExamName" id="examName" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
              </div>
              <div>
                <label for="totalDuration" class="block text-sm font-medium text-gray-700">Total Duration (minutes)</label>
                <input type="number" v-model="modal.data.TotalDuration" id="totalDuration" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
              </div>
              <div>
                <label for="examDate" class="block text-sm font-medium text-gray-700">Exam Date</label>
                <input type="date" v-model="modal.data.ExamDate" id="examDate" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
              </div>
            </div>
          </fieldset>
          
          <div class="flex justify-end space-x-4 pt-4">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="!modal.data.ChapterID && !modal.isEditMode">
              {{ modal.isEditMode ? 'Update Exam' : 'Save Exam' }}
            </button>
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
  </AdminLayout>
</template>

<script>
import apiService from '@/services/apiService';
import AdminLayout from '@/components/AdminLayout.vue';

export default {
  name: 'ExamsView',
  components: { AdminLayout },
  props: ['chapterId'],
  data() {
    return {
      // For the list
      loading: true,
      error: null,
      exams: [],
      // For the modals
      isModalOpen: false,
      isDeleteModalOpen: false,
      examToDelete: null,
      // For the create/edit form
      subjects: [],
      chapters: [],
      modal: {
        isEditMode: false,
        selectedSubjectId: '',
        subjectConfirmed: false,
        data: {},
      },
    };
  },
  watch: {
    chapterId() {
      this.loadExams();
    }
  },
  mounted() {
    this.loadExams();
  },
  methods: {
    // --- List Methods ---
    loadExams() {
      if (this.chapterId && Number(this.chapterId) > 0) {
        this.fetchExamsForChapter();
      } else {
        this.fetchAllExams();
      }
    },
    async fetchExamsForChapter() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiService.getExams(this.chapterId);
        this.exams = response.data;
      } catch (err) {
        this.error = 'Failed to load exams for this chapter.';
      } finally {
        this.loading = false;
      } 
    },
    async fetchAllExams() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiService.getExams(); 
        this.exams = response.data;
      } catch (err) {
        this.error = 'Failed to load all exams.';
      } finally {
        this.loading = false;
      }
    },
    viewQuestions(exam) {
      this.$router.push({ 
        name: 'Questions', 
        params: { examId: exam.ExamID },
        query: { 
          examName: exam.ExamName,
          chapterName: this.chapterId ? this.$route.query.chapterName : exam.ChapterName,
          subjectName: this.chapterId ? this.$route.query.subjectName : exam.SubjectName 
        }
      });
    },

    // --- Modal & Form Methods ---
    resetModal() {
      this.modal = {
        isEditMode: false,
        selectedSubjectId: '',
        subjectConfirmed: false,
        data: {
          ExamName: '',
          TotalDuration: 60,
          ExamDate: '',
          ChapterID: null,
        }
      };
      this.chapters = [];
    },
    closeModal() {
      this.isModalOpen = false;
    },
    async openAddModal() {
      this.resetModal();
      await this.fetchSubjects();
      this.isModalOpen = true;
    },
    openEditModal(exam) {
      this.resetModal();
      this.modal.isEditMode = true;
      // In edit mode, we assume the chapter context is fixed.
      this.modal.subjectConfirmed = true; 
      this.modal.data = { ...exam };
      if(this.modal.data.ExamDate) {
          this.modal.data.ExamDate = new Date(this.modal.data.ExamDate).toISOString().split('T')[0];
      }
      this.isModalOpen = true;
    },
    async fetchSubjects() {
      try {
        const response = await apiService.getSubjects();
        this.subjects = response.data;
      } catch (err) {
        this.error = "Failed to load subjects.";
      }
    },
    async confirmSubject() {
      if (!this.modal.selectedSubjectId) return;
      this.modal.subjectConfirmed = true;
      try {
        const response = await apiService.getChapters(this.modal.selectedSubjectId);
        this.chapters = response.data;
      } catch (err) {
        this.error = "Failed to load chapters for this subject.";
        this.modal.subjectConfirmed = false;
      }
    },
    changeSubject() {
      this.modal.subjectConfirmed = false;
      this.chapters = [];
      this.modal.data.ChapterID = null;
      this.modal.selectedSubjectId = '';
    },
    async handleFormSubmit() {
      const examData = {
        ExamName: this.modal.data.ExamName,
        TotalDuration: parseInt(this.modal.data.TotalDuration),
        ExamDate: this.modal.data.ExamDate,
      };

      try {
        if (this.modal.isEditMode) {
          await apiService.updateExam(this.modal.data.ExamID, examData);
        } else {
          await apiService.createExam(this.modal.data.ChapterID, examData);
        }
        this.loadExams();
        this.closeModal();
      } catch (err) {
        this.error = `Failed to ${this.modal.isEditMode ? 'update' : 'create'} exam.`;
      }
    },

    // --- Delete Methods ---
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
        this.loadExams();
        this.closeDeleteModal();
      } catch (err) {
        this.error = 'Failed to delete exam.';
      }
    }
  },
};
</script>