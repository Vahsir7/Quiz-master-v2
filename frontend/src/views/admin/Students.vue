<template>
  <AdminLayout>
    <template #header-title>
      Manage Students
    </template>

    <div v-if="loading" class="text-center">Loading students...</div>
    <div v-if="error" class="text-center text-red-500 p-4 bg-red-100 rounded-md">{{ error }}</div>

    <!-- Students Table -->
    <div v-if="!loading && !error" class="bg-white shadow-lg rounded-lg overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="student in students" :key="student.StudentID">
            <td class="px-6 py-4 font-medium">{{ student.Name }}</td>
            <td class="px-6 py-4 text-sm text-gray-500">{{ student.Email }}</td>
            <td class="px-6 py-4 text-right space-x-4">
              <button @click="openDetailsModal(student)" class="text-blue-600 hover:text-blue-800" title="View More Details">
                <i class="fas fa-eye"></i>
              </button>
              <button @click="openDeleteModal(student)" class="text-red-600 hover:text-red-800" title="Delete Student">
                <i class="fas fa-trash-alt"></i>
              </button>
            </td>
          </tr>
          <tr v-if="students.length === 0">
            <td colspan="3" class="px-6 py-4 text-center text-gray-500">No students found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- View More Details Modal -->
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

    <!-- Delete Confirmation Modal -->
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

  </AdminLayout>
</template>

<script>
import apiService from '@/services/apiService';
import AdminLayout from '@/components/AdminLayout.vue';

export default {
  name: 'StudentsView',
  components: { AdminLayout },
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
  },
};
</script>
