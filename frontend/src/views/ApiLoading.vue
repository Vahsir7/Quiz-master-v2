<template>
  <div class="loading-container">
    <div class="spinner"></div>
    <h2>⏳ Waking up the backend...</h2>
    <p>This may take ~60s if the Render server was inactive.</p>
  </div>
</template>

<script>
import apiService from "../services/apiService";

export default {
  name: "ApiLoading",
  data() {
    return {
      intervalId: null,
    };
  },
  mounted() {
    // Call the backend immediately and then every 5 seconds.
    this.wakeBackend();
    this.intervalId = setInterval(this.wakeBackend, 5000);
  },
  beforeUnmount() {
    // Clear the interval when the component is destroyed to prevent memory leaks.
    clearInterval(this.intervalId);
  },
  methods: {
    async wakeBackend() {
      try {
        await apiService.apiHealthCheck();
        // If the call succeeds, clear the interval and navigate to the login page.
        clearInterval(this.intervalId);
        this.$router.push("/login");
      } catch (err) {
        console.error("Wake failed, retrying in 5 seconds...", err);
      }
    },
  },
};
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-family: sans-serif;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #09f;
  margin-bottom: 1rem;

  animation: spin 1s ease infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
