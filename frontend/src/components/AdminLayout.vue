<template>
  <div class="admin-layout">
    <AdminNavbar />
    <div class="main-content">
      <RouterView />
    </div>
  </div>
</template>

<script>
import AdminNavbar from '@/components/AdminNavbar.vue';

export default {
  name: 'AdminLayout',
  components: {
    AdminNavbar
  }
}
</script>

<style>
@import '@/assets/admin.css';
</style>
