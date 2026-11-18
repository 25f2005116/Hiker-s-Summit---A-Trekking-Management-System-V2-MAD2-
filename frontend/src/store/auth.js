import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    role: localStorage.getItem('role') || null,
    message: null,
    messageType: 'info'
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.role === 'Admin',
    isStaff: (state) => state.role === 'Staff',
    isUser: (state) => state.role === 'User'
  },
  actions: {
    initAuth() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      }
    },
    async login(username, password) {
      try {
        const response = await axios.post('/api/auth/login', { username, password })
        this.token = response.data.access_token
        this.user = response.data.user
        this.role = response.data.user.role

        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        localStorage.setItem('role', this.role)

        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        this.setMessage('Login successful!', 'success')
        return { success: true, role: this.role }
      } catch (error) {
        const msg = error.response?.data?.error || 'Login failed. Please check credentials.'
        this.setMessage(msg, 'danger')
        return { success: false, error: msg }
      }
    },
    async register(username, password, contact_details) {
      try {
        const response = await axios.post('/api/auth/register', {
          username,
          password,
          contact_details
        })
        this.setMessage(response.data.message || 'Registration successful! Please log in.', 'success')
        return { success: true }
      } catch (error) {
        const msg = error.response?.data?.error || 'Registration failed.'
        this.setMessage(msg, 'danger')
        return { success: false, error: msg }
      }
    },
    logout() {
      this.token = null
      this.user = null
      this.role = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('role')
      delete axios.defaults.headers.common['Authorization']
      this.setMessage('Logged out successfully.', 'info')
    },
    setMessage(msg, type = 'info') {
      this.message = msg
      this.messageType = type
      setTimeout(() => {
        if (this.message === msg) {
          this.message = null
        }
      }, 5000)
    }
  }
})
