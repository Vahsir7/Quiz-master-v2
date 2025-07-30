<template>
  <StudentLayout>
    <div class="dashboard-header">
      <h2>My Profile</h2>
      <p>View and update your personal information.</p>
    </div>

    <div v-if="loading" class="text-center">Loading profile...</div>
    <div v-if="error" class="error-box">{{ error }}</div>

    <div v-if="!loading && formData" class="profile-container">
      <form @submit.prevent="handleUpdate" class="profile-form">
        <div v-if="successMessage" class="success-box">{{ successMessage }}</div>
        <div class="form-grid">
          <div class="form-group">
            <label for="name">Full Name</label>
            <input type="text" id="name" v-model="formData.name" class="form-input" :disabled="!isEditMode">
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="formData.email" class="form-input" :disabled="!isEditMode">
          </div>
          <div class="form-group">
            <label for="dob">Date of Birth</label>
            <input type="date" id="dob" v-model="formData.dob" class="form-input" :disabled="!isEditMode">
          </div>
          <div class="form-group">
            <label for="college_name">College Name</label>
            <input type="text" id="college_name" v-model="formData.college_name" class="form-input" :disabled="!isEditMode">
          </div>
          <div class="form-group">
            <label for="degree">Degree</label>
            <input type="text" id="degree" v-model="formData.degree" class="form-input" :disabled="!isEditMode">
          </div>
        </div>
        <div class="form-actions">
          <button v-if="!isEditMode" @click="enableEditMode" type="button" class="btn-primary">Edit Profile</button>
          <div v-if="isEditMode">
            <button @click="cancelUpdate" type="button" class="btn btn-secondary mr-2">Cancel</button>
            <button type="submit" class="btn-primary">Save Changes</button>
          </div>
        </div>
      </form>

      <div class="delete-section">
        <h3>Delete Account</h3>
        <p>Permanently delete your account and all associated data. This action cannot be undone.</p>
        <button @click="openDeleteModal" class="btn-danger">Delete My Account</button>
      </div>
    </div>

    <div v-if="isDeleteModalOpen" class="modal-overlay">
      <div class="modal-content text-center">
        <h3 class="text-lg font-medium">Are you sure?</h3>
        <p class="text-sm text-gray-500 mt-2">Do you really want to delete your account? All of your data will be permanently removed.</p>
        <div class="flex justify-center space-x-4 mt-6">
          <button @click="closeDeleteModal" class="btn btn-secondary">Cancel</button>
          <button @click="handleDelete" class="btn-danger">Delete</button>
        </div>
      </div>
    </div>
  </StudentLayout>
</template>

<script>
import StudentLayout from '@/components/StudentLayout.vue';
import apiService from '@/services/apiService';

export default {
  name: 'StudentProfile',
  components: { StudentLayout },
  data() {
    return {
      loading: true,
      error: null,
      successMessage: '',
      formData: null,
      originalFormData: null, // To store a backup of the data
      isEditMode: false,
      isDeleteModalOpen: false,
    };
  },
  async mounted() {
    this.fetchProfile();
  },
  methods: {
    async fetchProfile() {
      try {
        const response = await apiService.getStudentProfile();
        this.formData = response.data;
      } catch (err) {
        this.error = 'Failed to load your profile.';
      } finally {
        this.loading = false;
      }
    },
    enableEditMode() {
      // Create a backup of the current data before editing
      this.originalFormData = { ...this.formData };
      this.isEditMode = true;
    },
    cancelUpdate() {
      // Restore the original data and exit edit mode
      this.formData = { ...this.originalFormData };
      this.isEditMode = false;
      this.error = null;
      this.successMessage = '';
    },
    async handleUpdate() {
      this.error = null;
      this.successMessage = '';
      try {
        const response = await apiService.updateStudentProfile(this.formData);
        this.successMessage = response.data.message;
        this.isEditMode = false; // Disable edit mode after successful update
      } catch (err) {
        this.error = 'Failed to update your profile.';
      }
    },
    openDeleteModal() {
      this.isDeleteModalOpen = true;
    },
    closeDeleteModal() {
      this.isDeleteModalOpen = false;
    },
    async handleDelete() {
      try {
        await apiService.deleteStudentProfile();
        apiService.logout();
        this.$router.push('/login');
      } catch (err) {
        this.error = 'Failed to delete your account.';
        this.closeDeleteModal();
      }
    },
  },
};
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: auto;
}
.profile-form, .delete-section {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 1.5rem;
}
@media (min-width: 768px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
}
.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 5px;
}
.form-input:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}
.form-actions {
  margin-top: 2rem;
  text-align: right;
}
.btn-primary {
  background-color: #3498db;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 5px;
  border: none;
  cursor: pointer;
}
.btn-danger {
  background-color: #e74c3c;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 5px;
  border: none;
  cursor: pointer;
}
.delete-section {
  margin-top: 2rem;
  border-top: 2px solid #e74c3c;
}
.delete-section h3 {
  font-size: 1.25rem;
  font-weight: bold;
  color: #e74c3c;
}
.delete-section p {
  margin: 0.5rem 0 1rem;
  color: #7f8c8d;
}
.success-box {
  background-color: #2ecc71;
  color: white;
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 1.5rem;
}
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 50;
}
.modal-content {
  background-color: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  width: 100%;
  max-width: 400px;
}
.btn {
  font-weight: bold;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
}
.btn-secondary {
  background-color: #e5e7eb;
  color: #1f2937;
}
</style>