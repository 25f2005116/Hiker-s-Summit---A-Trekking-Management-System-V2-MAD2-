<template>
  <div class="container mt-5">
    <h1 class="text-center text-success mb-4">
      Edit Profile
    </h1>

    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card shadow bg-white bg-opacity-75">
          <div class="card-body">
            <form @submit.prevent="updateProfile">
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input
                  type="text"
                  :value="profile.username"
                  class="form-control"
                  disabled
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Contact Details (Email / Phone)</label>
                <input
                  v-model="profile.contact_details"
                  type="text"
                  class="form-control"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">New Password</label>
                <input
                  v-model="newPassword"
                  type="password"
                  class="form-control"
                  placeholder="Enter new password (optional)"
                  minlength="6"
                />
              </div>

              <div class="text-center">
                <input
                  type="submit"
                  value="Update Profile"
                  class="btn btn-success"
                  :disabled="loading"
                />
              </div>
            </form>
          </div>

          <router-link to="/dashboard" class="btn btn-secondary mt-2">
            Back to Dashboard
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../store/auth'

const authStore = useAuthStore()

const profile = ref({
  username: '',
  contact_details: ''
})
const newPassword = ref('')
const loading = ref(false)

async function fetchProfile() {
  try {
    const res = await axios.get('/api/auth/profile')
    profile.value = res.data
  } catch (err) {
    authStore.setMessage('Failed to load profile', 'danger')
  }
}

async function updateProfile() {
  loading.value = true
  try {
    const payload = {
      contact_details: profile.value.contact_details
    }
    if (newPassword.value.trim()) {
      payload.password = newPassword.value.trim()
    }

    const res = await axios.put('/api/auth/profile', payload)
    authStore.setMessage(res.data.message || 'Profile updated successfully', 'success')
    newPassword.value = ''
    await fetchProfile()
  } catch (err) {
    authStore.setMessage(err.response?.data?.error || 'Profile update failed', 'danger')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>
