<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-header">
        <i class="fas fa-graduation-cap auth-header__icon"></i>
        <h1 class="auth-header__title">Welcome to QuizMaster v2</h1>
        <p class="auth-header__subtitle">Please sign in to continue</p>
      </div>

      <div class="auth-card">
        <form @submit.prevent="handleLogin">
          <div v-if="error" class="error-message">
            {{ error }}
          </div>
          <div class="form-group">
            <label for="userType">Login as</label>
            <select id="userType" v-model="userType" class="form-select">
              <option value="student">Student</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div class="form-group">
            <label for="email">Email address</label>
            <input id="email" type="email" v-model="email" required autocomplete="email" class="form-input">
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input id="password" type="password" v-model="password" required autocomplete="current-password" class="form-input">
          </div>

          <div class="form-group">
            <button type="submit" :disabled="isLoading" class="btn-submit">
              <span v-if="isLoading">Signing in...</span>
              <span v-else>Sign in</span>
            </button>
          </div>
        </form>

        <div class="auth-footer">
          <p>
            Don't have an account?
            <router-link to="/register">
              Register here
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from '@/services/apiService';

export default {
  name: 'LoginView',
  data() {
    return {
      userType: 'student',
      email: '',
      password: '',
      error: null,
      isLoading: false,
    };
  },
  methods: {
    async handleLogin() {
      this.isLoading = true;
      this.error = null;
      try {
        const credentials = {
          type: this.userType,
          email: this.email,
          password: this.password,
        };
        const response = await apiService.login(credentials);

        localStorage.setItem('token', response.data.token);
        localStorage.setItem('userType', this.userType);

        if (this.userType === 'admin') {
          this.$router.push('/admin/dashboard');
        } else {
          localStorage.setItem('student_id', response.data.student_id);
          this.$router.push('/student/dashboard');
        }

      } catch (error) {
        if (error.response && error.response.data && error.response.data.message) {
          this.error = error.response.data.message;
        } else {
          this.error = 'An unexpected error occurred. Please try again.';
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
