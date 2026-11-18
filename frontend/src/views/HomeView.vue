<template>
  <div class="container mt-5">
    <!-- Exact MAD-1 Welcome Card from index.html -->
    <div class="card shadow bg-white bg-opacity-75">
      <div class="card-body text-center">
        <h1 class="text-success fw-bold">
          Welcome to Hiker's Summit
        </h1>
        <hr />
        <p class="lead">
          Plan, organize and experience unforgettable trekking adventures with our Trekking Management Application.
        </p>
      </div>
    </div>

    <!-- Action Buttons (Exact MAD-1 layout) -->
    <div class="text-center mt-4 mb-5">
      <!-- If already logged in: Direct link to user's dashboard -->
      <template v-if="authStore.isAuthenticated">
        <router-link :to="dashboardLink" class="btn btn-success px-4 py-2 fw-bold shadow">
          Go to {{ authStore.role }} Dashboard
        </router-link>
      </template>

      <!-- If guest: Show Login and Register -->
      <template v-else>
        <router-link to="/login" class="btn btn-success me-2">
          Login
        </router-link>
        <router-link to="/register" class="btn btn-success me-2">
          Register as a Member
        </router-link>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../store/auth'

const authStore = useAuthStore()

const dashboardLink = computed(() => {
  if (authStore.isAdmin) return '/admin'
  if (authStore.isStaff) return '/staff'
  if (authStore.isUser) return '/dashboard'
  return '/'
})
</script>
