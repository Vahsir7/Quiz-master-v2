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

<style scoped>
@import '@/assets/student.css';

.student-sidebar {
  width: 256px;
  background-color: #2c3e50; /* Dark blue-gray */
  color: white;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid #34495e;
  text-align: center;
}

.sidebar-title {
  font-size: 1.75rem;
  font-weight: bold;
}

.sidebar-nav {
  flex-grow: 1;
  padding-top: 1rem;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  color: #ecf0f1;
  text-decoration: none;
  transition: background-color 0.2s, color 0.2s;
  font-size: 1rem;
}

.nav-link:hover {
  background-color: #34495e;
}

.nav-link.router-link-exact-active {
  background-color: #3498db; /* Bright blue for active */
  color: white;
  font-weight: bold;
}

.nav-link i {
  margin-right: 1rem;
  width: 20px;
  text-align: center;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid #34495e;
}

.logout-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e74c3c;
  color: white;
  padding: 0.75rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 1rem;
  font-weight: 500;
}

.logout-button:hover {
  background-color: #c0392b;
}

.logout-button i {
  margin-right: 0.5rem;
}
</style>