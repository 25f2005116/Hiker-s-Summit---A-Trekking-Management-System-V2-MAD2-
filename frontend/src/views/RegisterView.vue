<template>
  <div class="container mt-5">
    <h2 class="text-center text-success mb-4">
      Create Your Trek Account
    </h2>

    <div class="card shadow bg-white bg-opacity-75 mx-auto" style="max-width:450px;">
      <div class="card-body">
        <form @submit.prevent="handleRegister">
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
            <label class="form-label">Contact Details (Email or Phone)</label>
            <input
              v-model="contactDetails"
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
              minlength="6"
              required
            />
          </div>

          <div class="text-center">
            <input
              type="submit"
              :value="loading ? 'Registering...' : 'Register'"
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
const contactDetails = ref('')
const password = ref('')
const loading = ref(false)

async function handleRegister() {
  loading.value = true
  const res = await authStore.register(username.value, password.value, contactDetails.value)
  loading.value = false

  if (res.success) {
    router.push('/login')
  }
}
</script>
