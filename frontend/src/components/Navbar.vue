<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-success shadow-sm sticky-top">
    <div class="container">
      <router-link to="/" class="navbar-brand fw-bold d-flex align-items-center">
        <i class="bi bi-compass-fill me-2 fs-4"></i>
        <span>Hiker's Summit</span>
        <span class="badge bg-light text-success ms-2 fs-7">V2</span>
      </router-link>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarContent"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <router-link to="/" class="nav-link" active-class="active">
              <i class="bi bi-mountain me-1"></i> Browse Treks
            </router-link>
          </li>

          <!-- Role-based Dashboard Links -->
          <li v-if="authStore.isAdmin" class="nav-item">
            <router-link to="/admin" class="nav-link" active-class="active">
              <i class="bi bi-speedometer2 me-1"></i> Admin Portal
            </router-link>
          </li>
          <li v-if="authStore.isStaff" class="nav-item">
            <router-link to="/staff" class="nav-link" active-class="active">
              <i class="bi bi-person-badge me-1"></i> Staff Portal
            </router-link>
          </li>
          <li v-if="authStore.isUser" class="nav-item">
            <router-link to="/dashboard" class="nav-link" active-class="active">
              <i class="bi bi-journal-bookmark me-1"></i> My Bookings
            </router-link>
          </li>
        </ul>

        <div class="d-flex align-items-center gap-2">
          <template v-if="authStore.isAuthenticated">
            <router-link to="/profile" class="btn btn-outline-light btn-sm d-flex align-items-center">
              <i class="bi bi-person-circle me-1"></i>
              <span>{{ authStore.user?.username }}</span>
              <span class="badge bg-white text-dark ms-2">{{ authStore.role }}</span>
            </router-link>
            <button @click="handleLogout" class="btn btn-danger btn-sm">
              <i class="bi bi-box-arrow-right me-1"></i> Logout
            </button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn btn-outline-light btn-sm">
              <i class="bi bi-box-arrow-in-right me-1"></i> Login
            </router-link>
            <router-link to="/register" class="btn btn-light text-success btn-sm fw-semibold">
              <i class="bi bi-person-plus me-1"></i> Register
            </router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../store/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.fs-7 {
  font-size: 0.75rem;
}
</style>
