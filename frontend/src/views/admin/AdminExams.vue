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
      <div class="filter-bar">
        <div class="filter-group">
          <input type="text" v-model="filters.search" placeholder="Search by exam name..." class="form-input w-auto mr-4">
        </div>
        <div class="filter-group">
          <select v-model="filters.subject_id" @change="onSubjectChange" class="form-select">
            <option value="">All Subjects</option>
            <option v-for="subject in subjects" :key="subject.SubjectID" :value="subject.SubjectID">
              {{ subject.SubjectName }}
            </option>
          </select>
        </div>
        <div class="filter-group">
          <select v-model="filters.chapter_id" class="form-select" :disabled="!filters.subject_id">
            <option value="">All Chapters</option>
            <option v-for="chapter in chapters" :key="chapter.ChapterID" :value="chapter.ChapterID">
              {{ chapter.ChapterName }}
            </option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="text-center">Loading exams...</div>
      <div v-if="error" class="error-box">{{ error }}</div>

      <div v-if="!loading" class="data-table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Exam Name</th>
              <th>Subject</th>
              <th>Chapter</th>
              <th>Published</th>
              <th>Questions</th>
              <th>Duration</th>
              <th>Exam Date</th>
              <th class="actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="exam in filteredExams" :key="exam.ExamID">
              <td class="font-medium">{{ exam.ExamName }}</td>
              <td>{{ exam.SubjectName }}</td>
              <td>{{ exam.ChapterName }}</td>
              <td>
                <span :class="exam.Published ? 'text-success' : 'text-danger'">
                  {{ exam.Published ? 'Yes' : 'No' }}
                </span>
              </td>
              <td>{{ exam.TotalQuestions }}</td>
              <td>{{ exam.TotalDuration }} mins</td>
              <td>{{ new Date(exam.ExamDate).toLocaleDateString() }}</td>
              <td class="actions">
                <button @click="openPublishModal(exam)" class="icon-publish" :title="exam.Published ? 'Unpublish Exam' : 'Publish Exam'">
                  <i :class="exam.Published ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
                <button @click="manageQuestions(exam)" class="icon-edit" title="Manage Questions">
                  <i class="fas fa-list-ul"></i>
                </button>
                <button @click="openEditModal(exam)" class="icon-edit" title="Edit Exam" :disabled="exam.Published">
                  <i class="fas fa-pencil-alt"></i>
                </button>
                <button @click="openDeleteModal(exam)" class="icon-delete" title="Delete Exam" :disabled="exam.Published">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </td>
            </tr>
            <tr v-if="filteredExams.length === 0">
              <td colspan="8" class="text-center text-muted py-4">No exams found.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="isModalOpen" class="modal-overlay">
        <div class="modal-content max-w-2xl">
          <form @submit.prevent="handleFormSubmit">
            <div class="modal-header">
              {{ modal.isEditMode ? 'Edit Exam' : 'Add New Exam' }}
            </div>
            <div class="modal-body">
              <template v-if="!modal.isEditMode">
                <div class="form-group">
                  <label>Subject</label>
                  <select v-model="selectedSubject" @change="fetchChaptersForSubject(selectedSubject)" class="form-select">
                    <option disabled value="">Please select one</option>
                    <option v-for="subject in subjects" :key="subject.SubjectID" :value="subject.SubjectID">
                      {{ subject.SubjectName }}
                    </option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Chapter</label>
                  <select v-model="modal.data.ChapterID" class="form-select" :disabled="!selectedSubject">
                    <option disabled value="">Please select one</option>
                    <option v-for="chapter in chapters" :key="chapter.ChapterID" :value="chapter.ChapterID">
                      {{ chapter.ChapterName }}
                    </option>
                  </select>
                </div>
              </template>
              <div class="form-group">
                <label>Exam Name</label>
                <input type="text" v-model="modal.data.ExamName" class="form-input">
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="form-group">
                  <label>Total Duration (minutes)</label>
                  <input type="number" v-model="modal.data.TotalDuration" class="form-input">
                </div>
                <div class="form-group">
                  <label>Exam Date</label>
                  <input type="date" v-model="modal.data.ExamDate" class="form-input">
                </div>
              </div>
              <div class="form-group">
                <label>Exam Type</label>
                <select v-model="modal.data.ExamType" class="form-select">
                  <option value="deadline">Deadline</option>
                  <option value="specific_time">Specific Time</option>
                </select>
              </div>
              <div v-if="modal.data.ExamType === 'specific_time'" class="form-group">
                <label>Start Time</label>
                <input type="time" v-model="modal.data.StartTime" class="form-input">
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" class="btn btn-primary">Save Exam</button>
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
            <h3 class="text-lg font-medium text-gray-900 mt-5">Delete Exam</h3>
            <p class="text-sm text-gray-500 mt-2">Are you sure you want to delete "{{ examToDelete.ExamName }}"?</p>
          </div>
          <div class="modal-footer justify-center">
            <button @click="closeDeleteModal" class="btn btn-secondary">Cancel</button>
            <button @click="confirmDelete" class="btn btn-danger">Delete</button>
          </div>
        </div>
      </div>

      <div v-if="isPublishModalOpen" class="modal-overlay">
        <div class="modal-content text-center">
          <div class="modal-body">
            <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100">
              <i class="fas fa-exclamation-triangle text-yellow-600 text-xl"></i>
            </div>
            <h3 class="text-lg font-medium text-gray-900 mt-5">Confirm Action</h3>
            <p class="text-sm text-gray-500 mt-2">Are you sure you want to {{ examToPublish.Published ? 'unpublish' : 'publish' }} the exam "{{ examToPublish.ExamName }}"?</p>
          </div>
          <div class="modal-footer justify-center">
            <button @click="closePublishModal" class="btn btn-secondary">Cancel</button>
            <button @click="confirmPublish" class="btn btn-primary">Confirm</button>
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
      filters: {
        search: '',
        subject_id: '',
        chapter_id: ''
      },
      isModalOpen: false,
      isDeleteModalOpen: false,
      isPublishModalOpen: false,
      modal: {
        isEditMode: false,
        data: {
            ExamType: 'deadline',
        },
      },
      examToDelete: null,
      examToPublish: null,
    };
  },
  computed: {
    filteredExams() {
      let filtered = this.exams;

      // Filter by search query
      if (this.filters.search) {
        const lowerCaseSearch = this.filters.search.toLowerCase();
        filtered = filtered.filter(exam =>
          exam.ExamName.toLowerCase().includes(lowerCaseSearch)
        );
      }

      // Filter by subject
      if (this.filters.subject_id) {
        filtered = filtered.filter(exam => exam.SubjectID === this.filters.subject_id);
      }

      // Filter by chapter
      if (this.filters.chapter_id) {
        filtered = filtered.filter(exam => exam.ChapterID === this.filters.chapter_id);
      }

      return filtered;
    }
  },
  async mounted() {
    this.fetchAllData();
  },
  methods: {
    async fetchAllData() {
      this.loading = true;
      this.error = null;
      try {
        const [examsRes, subjectsRes] = await Promise.all([
          apiService.getExams(),
          apiService.getSubjects()
        ]);
        this.exams = examsRes.data;
        this.subjects = subjectsRes.data;
      } catch (err) {
        this.error = 'Failed to load page data.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async fetchChaptersForSubject(subjectId) {
      if (!subjectId) {
        this.chapters = [];
        return;
      }
      try {
        const response = await apiService.getChapters(subjectId);
        this.chapters = response.data;
      } catch (err) {
        console.error('Failed to load chapters for selected subject.');
      }
    },
    onSubjectChange() {
      this.filters.chapter_id = '';
      if (this.filters.subject_id) {
        this.fetchChaptersForSubject(this.filters.subject_id);
      } else {
        this.chapters = [];
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
          ExamType: 'deadline',
          StartTime: '',
          Published: false,
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
        this.fetchAllData(); // Refetch all data
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
        this.fetchAllData(); // Refetch all data
        this.closeDeleteModal();
      } catch (err) {
        this.error = 'Failed to delete exam.';
        console.error(err);
      }
    },
    openPublishModal(exam) {
      this.examToPublish = exam;
      this.isPublishModalOpen = true;
    },
    closePublishModal() {
      this.isPublishModalOpen = false;
      this.examToPublish = null;
    },
    async confirmPublish() {
      if (!this.examToPublish) return;
      try {
        await apiService.publishExam(this.examToPublish.ExamID);
        // Find the exam and update its published status locally for immediate feedback
        const exam = this.exams.find(e => e.ExamID === this.examToPublish.ExamID);
        if (exam) {
            exam.Published = !exam.Published;
        }
      } catch (err) {
        this.error = `Failed to ${this.examToPublish.Published ? 'unpublish' : 'publish'} exam.`;
        console.error(err);
      } finally {
        this.closePublishModal();
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
