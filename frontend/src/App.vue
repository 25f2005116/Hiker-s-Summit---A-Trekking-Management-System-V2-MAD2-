<template>
  <div :class="['app-layout', isHome ? 'bg-home' : 'bg-common']">
    <!-- Navbar with Role-Aware Dashboard Link -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-success bg-opacity-75 shadow-sm">
      <div class="container">
        <!-- Clicking Hiker's Summit takes logged-in users straight to their dashboard -->
        <router-link :to="dashboardLink" class="navbar-brand fw-bold text-white">
          Hiker's Summit
        </router-link>

        <!-- Extra header buttons hidden on home page to keep UI clean and exact to MAD-1 -->
        <div class="d-flex align-items-center gap-2" v-if="!isHome">
          <template v-if="authStore.isAuthenticated">
            <span class="text-white small me-2">
              Signed in as: <strong>{{ authStore.user?.username }}</strong> ({{ authStore.role }})
            </span>
            <router-link :to="dashboardLink" class="btn btn-light text-success btn-sm fw-semibold">
              Dashboard
            </router-link>
            <button @click="handleLogout" class="btn btn-outline-light btn-sm">
              Logout
            </button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn btn-outline-light btn-sm">
              Login
            </router-link>
            <router-link to="/register" class="btn btn-light text-success btn-sm fw-semibold">
              Register
            </router-link>
          </template>
        </div>
      </div>
    </nav>

    <!-- Global In-Page Alert Banner -->
    <div v-if="authStore.message" class="container mt-3">
      <div
        :class="['alert', `alert-${authStore.messageType}`, 'alert-dismissible', 'fade', 'show', 'shadow']"
        role="alert"
      >
        <span>{{ authStore.message }}</span>
        <button
          type="button"
          class="btn-close"
          @click="authStore.message = null"
          aria-label="Close"
        ></button>
      </div>
    </div>

    <!-- Main Content Area -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- Exact MAD-1 Footer -->
    <footer class="text-center py-3 mt-5 text-white">
      <hr class="border-light" />
      © 2026 Hiker's Summit | Trekking Management System
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './store/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isHome = computed(() => route.path === '/')

// Smart Dashboard Link: /admin for Admin, /staff for Staff, /dashboard for User
const dashboardLink = computed(() => {
  if (authStore.isAdmin) return '/admin'
  if (authStore.isStaff) return '/staff'
  if (authStore.isUser) return '/dashboard'
  return '/'
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.bg-home {
  background-image: url("/images/background.jpg");
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
}

.bg-common {
  background-image: url("/images/common.png");
  background-size: cover;
  background-position: bottom center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

.main-content {
  flex: 1 0 auto;
}
</style>
