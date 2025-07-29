<template>
  <div class="student-layout">
    <aside class="student-sidebar">
      <div class="sidebar-header">
        <h1 class="sidebar-title">QuizMaster</h1>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/student/dashboard" class="nav-link">
          <i class="fas fa-tachometer-alt"></i> Dashboard
        </router-link>
        <router-link to="/student/exams" class="nav-link">
          <i class="fas fa-file-alt"></i> Exams
        </router-link>
        <router-link to="/student/history" class="nav-link">
          <i class="fas fa-history"></i> History
        </router-link>
        <router-link to="/student/profile" class="nav-link">
          <i class="fas fa-user-cog"></i> Profile
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <button @click="logout" class="logout-button">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </aside>

    <div class="main-content">
      <main class="content-main">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentLayout',
  methods: {
    logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('userType');
      this.$router.push('/login');
    }
  }
}
</script>

<style>
@import '@/assets/student.css';
</style>
