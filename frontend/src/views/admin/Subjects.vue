<template>
  <div>
    <header class="content-header">
      <h2 class="content-header__title">Manage Subjects</h2>
      <div class="header-actions">
        <input type="text" v-model="search" placeholder="Search Subjects..." @input="fetchSubjects" class="form-input w-auto">
        <button @click="openAddModal" class="btn btn-primary">
          <i class="fas fa-plus"></i> Add New Subject
        </button>
      </div>
    </header>

    <main class="content-main">
      <div v-if="loading">Loading subjects...</div>
      <div v-if="error" class="error-box">{{ error }}</div>

      <div v-if="!loading && !error" class="data-table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Subject Name</th>
              <th>Description</th>
              <th class="actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="subject in subjects" :key="subject.SubjectID">
              <td>{{ subject.SubjectName }}</td>
              <td>{{ subject.Description }}</td>
              <td class="actions">
                <button @click="viewChapters(subject)" class="icon-add" title="View Chapters"><i class="fas fa-list-ul"></i></button>
                <button @click="openEditModal(subject)" class="icon-edit" title="Edit Subject"><i class="fas fa-pencil-alt"></i></button>
                <button @click="openDeleteModal(subject)" class="icon-delete" title="Delete Subject"><i class="fas fa-trash-alt"></i></button>
              </td>
            </tr>
            <tr v-if="subjects.length === 0">
              <td colspan="3" style="text-align: center;">No subjects found.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="isModalOpen" class="modal-overlay">
        <div class="modal-content">
          <form @submit.prevent="handleFormSubmit">
            <div class="modal-header">
              {{ modal.isEditMode ? 'Edit Subject' : 'Add New Subject' }}
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label for="subjectName">Subject Name</label>
                <input type="text" id="subjectName" v-model="modal.data.SubjectName" class="form-input" required>
              </div>
              <div class="form-group">
                <label for="subjectDescription">Description</label>
                <textarea id="subjectDescription" v-model="modal.data.Description" rows="3" class="form-textarea"></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" class="btn btn-primary">{{ modal.isEditMode ? 'Update' : 'Create' }}</button>
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
              <h3 class="text-lg font-medium text-gray-900 mt-5">Delete Subject</h3>
              <p class="text-sm text-gray-500 mt-2">Are you sure you want to delete "{{ subjectToDelete.SubjectName }}"?</p>
            </div>
            <div class="modal-footer justify-center">
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
  name: 'SubjectsView',
  data() {
    return {
      loading: true,
      error: null,
      subjects: [],
      search: '',
      isModalOpen: false,
      isDeleteModalOpen: false,
      modal: {
        isEditMode: false,
        data: {
          SubjectID: null,
          SubjectName: '',
          Description: ''
        }
      },
      subjectToDelete: null,
    };
  },
  async mounted() {
    this.fetchSubjects();
  },
  methods: {
    async fetchSubjects() {
      this.loading = true;
      try {
        const response = await apiService.getSubjects(this.search);
        this.subjects = response.data;
      } catch (err) {
        this.error = 'Failed to load subjects.';
      } finally {
        this.loading = false;
      }
    },
    resetModal() {
      this.modal = {
        isEditMode: false,
        data: { SubjectID: null, SubjectName: '', Description: '' }
      };
    },
    openAddModal() {
      this.resetModal();
      this.isModalOpen = true;
    },
    openEditModal(subject) {
      this.resetModal();
      this.modal.isEditMode = true;
      this.modal.data = { ...subject };
      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
    },
    async handleFormSubmit() {
      try {
        if (this.modal.isEditMode) {
          await apiService.updateSubject(this.modal.data.SubjectID, this.modal.data);
        } else {
          await apiService.createSubject(this.modal.data);
        }
        this.fetchSubjects();
        this.closeModal();
      } catch (err) {
        this.error = `Failed to ${this.modal.isEditMode ? 'update' : 'create'} subject.`;
      }
    },
    openDeleteModal(subject) {
        this.subjectToDelete = subject;
        this.isDeleteModalOpen = true;
    },
    closeDeleteModal() {
        this.isDeleteModalOpen = false;
        this.subjectToDelete = null;
    },
    async confirmDelete() {
        if (!this.subjectToDelete) return;
        try {
            await apiService.deleteSubject(this.subjectToDelete.SubjectID);
            this.fetchSubjects();
            this.closeDeleteModal();
        } catch (err) {
            this.error = 'Failed to delete subject.';
        }
    },
    viewChapters(subject) {
        this.$router.push({
          name: 'Chapters',
          params: { subjectId: subject.SubjectID },
          query: {
            subjectName: subject.SubjectName,
            subjectDescription: subject.Description
          }
        });
    }
  },
};
</script>

