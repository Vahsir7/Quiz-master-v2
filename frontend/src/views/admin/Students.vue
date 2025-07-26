<template>
  <div>
    <header class="content-header">
      <h2 class="content-header__title">Manage Students</h2>
    </header>

    <main class="content-main">
      <div v-if="loading" class="text-center">Loading students...</div>
      <div v-if="error" class="text-center text-red-500 p-4 bg-red-100 rounded-md">{{ error }}</div>

      <div v-if="!loading && !error" class="data-table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th class="actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in students" :key="student.StudentID">
              <td>{{ student.Name }}</td>
              <td>{{ student.Email }}</td>
              <td class="actions">
                <button @click="openDetailsModal(student)" class="icon-edit" title="View More Details">
                  <i class="fas fa-eye"></i>
                </button>
                <button @click="sendMonthlyReport(student)" class="icon-publish" title="Send Monthly Report">
                  <i class="fas fa-paper-plane"></i>
                </button>
                <button @click="openDeleteModal(student)" class="icon-delete" title="Delete Student">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </td>
            </tr>
            <tr v-if="students.length === 0">
              <td colspan="3" class="text-center">No students found.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="isDetailsModalOpen" class="modal-overlay">
        <div class="modal-content max-w-lg">
          <h3 class="text-xl font-semibold mb-4">Student Details</h3>
          <div v-if="detailsLoading" class="text-center">Loading details...</div>
          <div v-else class="space-y-2 text-sm">
            <p><strong>ID:</strong> {{ selectedStudent.StudentID }}</p>
            <p><strong>Name:</strong> {{ selectedStudent.Name }}</p>
            <p><strong>Email:</strong> {{ selectedStudent.Email }}</p>
            <p><strong>Date of Birth:</strong> {{ selectedStudent.DOB }}</p>
            <p><strong>College:</strong> {{ selectedStudent.CollegeName }}</p>
            <p><strong>Degree:</strong> {{ selectedStudent.Degree }}</p>
          </div>
          <div class="flex justify-end mt-6">
            <button @click="closeDetailsModal" class="btn btn-secondary">Close</button>
          </div>
        </div>
      </div>

      <div v-if="isDeleteModalOpen" class="modal-overlay">
        <div class="modal-content text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <i class="fas fa-exclamation-triangle text-red-600 text-xl"></i>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mt-5">Delete Student</h3>
          <p class="text-sm text-gray-500 mt-2">Are you sure you want to delete "{{ studentToDelete.Name }}"? This action cannot be undone.</p>
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
  name: 'StudentsView',
  data() {
    return {
      loading: true,
      detailsLoading: false,
      error: null,
      students: [],
      selectedStudent: null,
      studentToDelete: null,
      isDetailsModalOpen: false,
      isDeleteModalOpen: false,
    };
  },
  mounted() {
    this.fetchStudents();
  },
  methods: {
    async fetchStudents() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiService.getStudents();
        this.students = response.data;
      } catch (err) {
        this.error = 'Failed to load students.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async openDetailsModal(student) {
      this.isDetailsModalOpen = true;
      this.detailsLoading = true;
      try {
        const response = await apiService.getStudents(student.StudentID);
        this.selectedStudent = response.data;
      } catch (err) {
        this.error = `Failed to load details for ${student.Name}.`;
        this.closeDetailsModal();
      } finally {
        this.detailsLoading = false;
      }
    },
    closeDetailsModal() {
      this.isDetailsModalOpen = false;
      this.selectedStudent = null;
    },
    openDeleteModal(student) {
      this.studentToDelete = student;
      this.isDeleteModalOpen = true;
    },
    closeDeleteModal() {
      this.isDeleteModalOpen = false;
      this.studentToDelete = null;
    },
    async confirmDelete() {
      if (!this.studentToDelete) return;
      try {
        await apiService.deleteStudent(this.studentToDelete.StudentID);
        this.fetchStudents(); // Refresh the list
      } catch (err) {
        this.error = 'Failed to delete student.';
        console.error(err);
      } finally {
        this.closeDeleteModal();
      }
    },
    async sendMonthlyReport(student) {
      try {
        await apiService.sendMonthlyReport(student.StudentID);
        alert(`A monthly report is being generated for ${student.Name}.`);
      } catch (err) {
        this.error = `Failed to trigger report for ${student.Name}.`;
      }
    },
  },
};
</script>
