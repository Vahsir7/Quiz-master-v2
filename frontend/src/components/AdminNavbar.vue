<template>
  <aside class="admin-navbar">
    <div class="navbar-header">
      <h1 class="navbar-title">QuizMaster</h1>
      <span class="navbar-subtitle">Admin Panel</span>
    </div>
    <nav class="navbar-nav">
      <router-link to="/admin/dashboard" class="nav-link">
        <i class="fas fa-tachometer-alt"></i> Dashboard
      </router-link>
      <router-link to="/admin/subjects" class="nav-link">
        <i class="fas fa-book"></i> Subjects
      </router-link>
      <router-link to="/admin/exams" class="nav-link">
        <i class="fas fa-file-alt"></i> Exams
      </router-link>
      <router-link to="/admin/students" class="nav-link">
        <i class="fas fa-users"></i> Students
      </router-link>
    </nav>
    <div class="navbar-footer">
      <button @click="logout" class="logout-button">
        <i class="fas fa-sign-out-alt"></i> Logout
      </button>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'AdminNavbar',
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
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

.admin-navbar {
  width: 256px; /* 64 * 4px = w-64 */
  background-color: #1f2937; /* gray-800 */
  color: white;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.navbar-header {
  padding: 1.5rem; /* px-6 py-4 */
  border-bottom: 1px solid #374151; /* border-gray-700 */
}

.navbar-title {
  font-size: 1.5rem; /* text-2xl */
  font-weight: bold;
}

.navbar-subtitle {
  font-size: 0.875rem; /* text-sm */
  color: #9ca3af; /* text-gray-400 */
}

.navbar-nav {
  flex-grow: 1; /* flex-grow */
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem; /* px-6 py-3 */
  color: #d1d5db; /* text-gray-300 */
  text-decoration: none;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: #374151; /* hover:bg-gray-700 */
}

/* Active link style */
.nav-link.router-link-exact-active {
  background-color: #374151; /* bg-gray-700 */
  color: white;
}

.nav-link i {
  margin-right: 0.75rem; /* mr-3 */
}

.navbar-footer {
  padding: 1rem 1.5rem; /* px-6 py-4 */
  border-top: 1px solid #374151; /* border-gray-700 */
}

.logout-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #dc2626; /* bg-red-600 */
  color: white;
  padding: 0.5rem 0; /* py-2 */
  border: none;
  border-radius: 0.375rem; /* rounded-md */
  cursor: pointer;
  transition: background-color 0.2s;
}

.logout-button:hover {
  background-color: #b91c1c; /* hover:bg-red-700 */
}

.logout-button i {
  margin-right: 0.5rem; /* mr-2 */
}
</style>