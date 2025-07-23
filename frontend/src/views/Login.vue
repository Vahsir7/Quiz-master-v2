<template>
  <div class="min-h-screen bg-gray-100 flex flex-col justify-center items-center p-4">
    <div class="max-w-md w-full bg-white rounded-lg shadow-xl p-8 space-y-6">
      <div class="text-center">
        <h1 class="text-4xl font-extrabold text-gray-800">Welcome to QuizMaster v2</h1>
        <p class="mt-2 text-gray-600">Please sign in to continue</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label for="userType" class="block text-sm font-medium text-gray-700">Login as</label>
          <select id="userType" v-model="userType" class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
            <option value="student">Student</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">Email address</label>
          <input id="email" type="email" v-model="email" required autocomplete="email" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
          <input id="password" type="password" v-model="password" required autocomplete="current-password" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
        </div>

        <div v-if="error" class="text-red-500 text-sm text-center">
          {{ error }}
        </div>

        <div>
          <button type="submit" :disabled="isLoading" class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-400">
            <span v-if="isLoading">Signing in...</span>
            <span v-else>Sign in</span>
          </button>
        </div>
      </form>
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
          // FIX: Store the student_id from the response
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
