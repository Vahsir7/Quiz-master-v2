<template>
  <div>
    <header class="content-header">
      <h2 class="content-header__title">Manage Chapters</h2>
      <div class="header-actions">
        <input type="text" v-model="search" placeholder="Search Chapters..." @input="fetchChapters" class="form-input w-auto">
        <button @click="openAddModal" class="btn btn-primary">
          <i class="fas fa-plus mr-2"></i> Add New Chapter
        </button>
      </div>
    </header>

    <main class="content-main">
      <div class="mb-4 p-4 border rounded-lg bg-gray-50">
          <h2 class="text-xl font-bold text-gray-800">Subject: {{ $route.query.subjectName || '...' }}</h2>
          <p class="text-sm text-gray-600 mt-1">{{ $route.query.subjectDescription || 'Chapters for the selected subject.' }}</p>
      </div>

      <div v-if="loading" class="text-center text-gray-600">Loading chapters...</div>
      <div v-if="error" class="error-box">{{ error }}</div>

      <div v-if="!loading && !error" class="data-table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Chapter Name</th>
              <th>Description</th>
              <th class="actions">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="chapter in chapters" :key="chapter.ChapterID">
              <td>{{ chapter.ChapterName }}</td>
              <td>{{ chapter.Description }}</td>
              <td class="actions">
                <button @click="viewExams(chapter)" class="icon-add" title="View/Add Exams"><i class="fas fa-file-alt"></i></button>
                <button @click="openEditModal(chapter)" class="icon-edit" title="Edit Chapter"><i class="fas fa-pencil-alt"></i></button>
                <button @click="openDeleteModal(chapter)" class="icon-delete" title="Delete Chapter"><i class="fas fa-trash-alt"></i></button>
              </td>
            </tr>
            <tr v-if="chapters.length === 0">
              <td colspan="3" class="text-center text-gray-500">No chapters found for this subject.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="isModalOpen" class="modal-overlay">
          <div class="modal-content">
            <form @submit.prevent="handleFormSubmit">
              <div class="modal-header">
                {{ modal.isEditMode ? 'Edit Chapter' : 'Add New Chapter' }}
              </div>
              <div class="modal-body">
                  <div class="form-group">
                      <label for="chapterName">Chapter Name</label>
                      <input type="text" id="chapterName" v-model="modal.data.ChapterName" class="form-input" required>
                  </div>
                  <div class="form-group">
                      <label for="chapterDescription">Description</label>
                      <textarea id="chapterDescription" v-model="modal.data.Description" rows="3" class="form-textarea"></textarea>
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
              <h3 class="text-lg font-medium text-gray-900 mt-5">Are you sure?</h3>
              <p class="text-sm text-gray-500 mt-2">Do you really want to delete the chapter "{{ chapterToDelete.ChapterName }}"?</p>
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
  name: 'ChaptersView',
  props: {
    subjectId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      loading: true,
      error: null,
      chapters: [],
      search: '',
      isModalOpen: false,
      isDeleteModalOpen: false,
      modal: {
        isEditMode: false,
        data: {
          ChapterID: null,
          ChapterName: '',
          Description: ''
        }
      },
      chapterToDelete: null,
    };
  },
  async mounted() {
    this.fetchChapters();
  },
  methods: {
    async fetchChapters() {
      this.loading = true;
      try {
        const response = await apiService.getChapters(this.subjectId, this.search);
        this.chapters = response.data;
      } catch (err) {
        this.error = 'Failed to load chapters for this subject.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    resetModal() {
      this.modal = {
        isEditMode: false,
        data: { ChapterID: null, ChapterName: '', Description: '' }
      };
    },
    openAddModal() {
      this.resetModal();
      this.isModalOpen = true;
    },
    openEditModal(chapter) {
      this.resetModal();
      this.modal.isEditMode = true;
      this.modal.data = { ...chapter };
      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
    },
    async handleFormSubmit() {
      try {
        if (this.modal.isEditMode) {
          await apiService.updateChapter(this.modal.data.ChapterID, this.modal.data);
        } else {
          await apiService.createChapter(this.subjectId, this.modal.data);
        }
        this.fetchChapters();
        this.closeModal();
      } catch (err) {
        this.error = `Failed to ${this.modal.isEditMode ? 'update' : 'create'} chapter.`;
        console.error(err);
      }
    },
    openDeleteModal(chapter) {
        this.chapterToDelete = chapter;
        this.isDeleteModalOpen = true;
    },
    closeDeleteModal() {
        this.isDeleteModalOpen = false;
        this.chapterToDelete = null;
    },
    async confirmDelete() {
        if (!this.chapterToDelete) return;
        try {
            await apiService.deleteChapter(this.chapterToDelete.ChapterID);
            this.fetchChapters();
            this.closeDeleteModal();
        } catch (err) {
            this.error = 'Failed to delete chapter.';
            console.error(err);
        }
    },
    viewExams(chapter) {
        this.$router.push({
        name: 'AdminExams',
        query: {
            chapterId: chapter.ChapterID,
            chapterName: chapter.ChapterName,
            subjectName: this.$route.query.subjectName
        }
     });
    }
  },
};
</script>
