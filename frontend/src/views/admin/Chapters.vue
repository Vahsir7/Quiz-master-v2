<template>
  <AdminLayout>
    <template #header-title>
      Manage Chapters
    </template>

    <template #header-actions>
      <button @click="openAddModal" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-lg flex items-center">
        <i class="fas fa-plus mr-2"></i> Add New Chapter
      </button>
    </template>
    
    <div class="mb-4 p-4 border rounded-lg bg-gray-50">
        <h2 class="text-xl font-bold text-gray-800">Subject: {{ $route.query.subjectName || '...' }}</h2>
        <p class="text-sm text-gray-600 mt-1">{{ $route.query.subjectDescription || 'Chapters for the selected subject.' }}</p>
    </div>

    <div v-if="loading" class="text-center text-gray-600">Loading chapters...</div>
    <div v-if="error" class="text-center text-red-500 p-4 bg-red-100 rounded-md">{{ error }}</div>

    <div v-if="!loading && !error" class="bg-white shadow-lg rounded-lg overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Chapter Name</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="chapter in chapters" :key="chapter.ChapterID" class="hover:bg-gray-50">
            <td class="px-6 py-4">{{ chapter.ChapterName }}</td>
            <td class="px-6 py-4">{{ chapter.Description }}</td>
            <td class="px-6 py-4 text-right space-x-4">
              <button @click="viewExams(chapter)" class="text-blue-600 hover:text-blue-800" title="View/Add Exams"><i class="fas fa-file-alt"></i></button>
              <button @click="openEditModal(chapter)" class="text-indigo-600 hover:text-indigo-800" title="Edit Chapter"><i class="fas fa-pencil-alt"></i></button>
              <button @click="openDeleteModal(chapter)" class="text-red-600 hover:text-red-800" title="Delete Chapter"><i class="fas fa-trash-alt"></i></button>
            </td>
          </tr>
          <tr v-if="chapters.length === 0">
            <td colspan="3" class="px-6 py-4 text-center text-gray-500">No chapters found for this subject.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isModalOpen" class="modal-overlay">
        <div class="modal-content">
            <h3 class="text-xl font-semibold mb-4">{{ modal.isEditMode ? 'Edit Chapter' : 'Add New Chapter' }}</h3>
            <form @submit.prevent="handleFormSubmit">
                <div class="mb-4">
                    <label for="chapterName" class="block text-sm font-medium text-gray-700">Chapter Name</label>
                    <input type="text" id="chapterName" v-model="modal.data.ChapterName" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
                </div>
                <div class="mb-4">
                    <label for="chapterDescription" class="block text-sm font-medium text-gray-700">Description</label>
                    <textarea id="chapterDescription" v-model="modal.data.Description" rows="3" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm"></textarea>
                </div>
                <div class="flex justify-end space-x-4">
                    <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
                    <button type="submit" class="btn btn-primary">{{ modal.isEditMode ? 'Update' : 'Create' }}</button>
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
            <p class="text-sm text-gray-500 mt-2">Do you really want to delete the chapter "{{ chapterToDelete.ChapterName }}"?</p>
            <div class="flex justify-center space-x-4 mt-6">
                <button @click="closeDeleteModal" class="btn btn-secondary">Cancel</button>
                <button @click="confirmDelete" class="btn btn-danger">Delete</button>
            </div>
        </div>
    </div>
  </AdminLayout>
</template>

<script>
import AdminLayout from '@/components/AdminLayout.vue';
import apiService from '@/services/apiService';

export default {
  name: 'ChaptersView',
  components: {
    AdminLayout
  },
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
        const response = await apiService.getChapters(this.subjectId);
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
        name: 'Exams',
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