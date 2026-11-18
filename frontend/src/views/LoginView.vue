<template>
  <div class="container mt-5">
    <h2 class="text-center text-success mb-4">
      Login To Your Trek Account
    </h2>

    <div class="card shadow bg-white bg-opacity-75 mx-auto" style="max-width:450px;">
      <div class="card-body">
        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label class="form-label">Username</label>
            <input
              v-model="username"
              type="text"
              class="form-control"
              required
            />
          </div>

          <div class="mb-3">
            <label class="form-label">Password</label>
            <input
              v-model="password"
              type="password"
              class="form-control"
              required
            />
          </div>

          <div class="text-center">
            <input
              type="submit"
              :value="loading ? 'Logging in...' : 'Login'"
              class="btn btn-success"
              :disabled="loading"
            />
          </div>
        </form>
      </div>

      <router-link to="/" class="btn btn-secondary">
        Back to Home
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const authStore = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  const res = await authStore.login(username.value, password.value)
  loading.value = false

  if (res.success) {
    if (res.role === 'Admin') router.push('/admin')
    else if (res.role === 'Staff') router.push('/staff')
    else router.push('/dashboard')
  }
}
</script>
