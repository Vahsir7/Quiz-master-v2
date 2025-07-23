<template>
  <div class="admin-layout">
    <AdminNavbar />
    <div class="main-content">
      <header class="content-header">
        <h2 class="content-header__title">
          <slot name="header-title">Default Title</slot>
        </h2>
        <div>
          <slot name="header-actions"></slot>
        </div>
      </header>
      <main class="content-main">
        <slot></slot>
      </main>
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
/* Import the central layout CSS */
@import '@/assets/admin.css';
</style>