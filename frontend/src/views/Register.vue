<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-header">
        <i class="fas fa-user-plus auth-header__icon"></i>
        <h1 class="auth-header__title">Create Your Student Account</h1>
        <p class="auth-header__subtitle">Join QuizMaster to start learning</p>
      </div>

      <div class="auth-card">
        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <form @submit.prevent="handleRegister">
          <div class="form-group">
            <label for="name">Full Name</label>
            <input id="name" type="text" v-model="formData.name" required class="form-input">
          </div>
          <div class="form-group">
            <label for="email">Email Address</label>
            <input id="email" type="email" v-model="formData.email" required class="form-input">
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input id="password" type="password" v-model="formData.password" required class="form-input">
          </div>
           <div class="form-group">
            <label for="dob">Date of Birth</label>
            <input id="dob" type="date" v-model="formData.dob" required class="form-input">
          </div>
           <div class="form-group">
            <label for="college_name">College Name</label>
            <input id="college_name" type="text" v-model="formData.college_name" required class="form-input">
          </div>
           <div class="form-group">
            <label for="degree">Degree</label>
            <input id="degree" type="text" v-model="formData.degree" required class="form-input">
          </div>

          <div class="form-group">
            <button type="submit" :disabled="isLoading" class="btn-submit">
              <span v-if="isLoading">Registering...</span>
              <span v-else>Register</span>
            </button>
          </div>
        </form>

        <div class="auth-footer">
          <p>
            Already have an account?
            <router-link to="/login">Login here</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from '@/services/apiService';

export default {
  name: 'RegisterView',
  data() {
    return {
      formData: {
        name: '',
        email: '',
        password: '',
        dob: '',
        college_name: '',
        degree: '',
      },
      error: null,
      successMessage: '',
      isLoading: false,
    };
  },
  methods: {
    async handleRegister() {
      this.isLoading = true;
      this.error = null;
      this.successMessage = '';
      try {
        await apiService.registerStudent(this.formData);
        this.successMessage = 'Registration successful! You will be redirected to the login page.';
        setTimeout(() => {
          this.$router.push('/login');
        }, 3000);
      } catch (err) {
        if (err.response && err.response.data && err.response.data.message) {
          this.error = err.response.data.message;
        } else {
          this.error = 'An unexpected error occurred during registration.';
        }
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>

<style scoped>
@import '@/assets/auth.css';
</style>
