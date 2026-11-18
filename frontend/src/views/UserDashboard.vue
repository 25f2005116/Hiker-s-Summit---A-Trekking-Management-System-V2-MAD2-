<template>
  <div class="container mt-5">
    <h1 class="text-center text-success mb-4">
      Welcome {{ authStore.user?.username }}
    </h1>

    <div class="row justify-content-center">
      <!-- Menu Card (Exact MAD-1 User_dash.html layout) -->
      <div class="col-md-6 mb-4">
        <div class="card shadow bg-white bg-opacity-75">
          <div class="card-body">
            <h3 class="text-success text-center">
              What do you want to do?
            </h3>
            <hr />

            <div class="d-grid gap-2">
              <button
                @click="activeView = 'available_treks'"
                :class="['btn', activeView === 'available_treks' ? 'btn-dark' : 'btn-success']"
              >
                View Available Treks
              </button>

              <button
                @click="activeView = 'search_treks'"
                :class="['btn', activeView === 'search_treks' ? 'btn-dark' : 'btn-success']"
              >
                Search Treks
              </button>

              <button
                @click="activeView = 'my_bookings'"
                :class="['btn', activeView === 'my_bookings' ? 'btn-dark' : 'btn-success']"
              >
                My Bookings ({{ activeBookings.length }})
              </button>

              <button
                @click="activeView = 'trekking_history'"
                :class="['btn', activeView === 'trekking_history' ? 'btn-dark' : 'btn-success']"
              >
                Trekking History ({{ historyTreks.length }})
              </button>

              <!-- MAD-2 User Triggered Async Job (Page 11 of PDF) -->
              <button
                @click="triggerExportCsv"
                class="btn btn-outline-success"
                :disabled="exportLoading"
              >
                <span v-if="exportLoading" class="spinner-border spinner-border-sm me-1"></span>
                <span>{{ exportLoading ? 'Triggering Export Batch Job...' : 'Export History (CSV)' }}</span>
              </button>

              <router-link to="/profile" class="btn btn-success">
                Edit Profile
              </router-link>

              <button @click="handleLogout" class="btn btn-danger">
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Ready Download Banner for CSV -->
    <div v-if="downloadUrl" class="alert alert-success alert-dismissible fade show shadow mx-auto" style="max-width: 800px;" role="alert">
      <strong>Batch Job Complete:</strong> Your booking history CSV is ready.
      <a :href="downloadUrl" download class="btn btn-sm btn-success ms-3 text-white">
        Download CSV File
      </a>
      <button type="button" class="btn-close" @click="downloadUrl = null"></button>
    </div>

    <!-- Active View Display (Tables from MAD-1) -->
    <div class="row justify-content-center mt-3">
      <div class="col-md-10">

        <!-- 1. View Available Treks -->
        <div v-if="activeView === 'available_treks'" class="card shadow bg-white bg-opacity-75 mb-4">
          <div class="card-body">
            <h3 class="text-success text-center mb-3">Available Treks</h3>
            <div class="table-responsive">
              <table class="table table-bordered table-striped table-hover align-middle">
                <thead class="table-success">
                  <tr>
                    <th>Trek Name</th>
                    <th>Location</th>
                    <th>Difficulty</th>
                    <th>Duration</th>
                    <th>Available Slots</th>
                    <th>Dates</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="t in openTreks" :key="t.id">
                    <td><strong>{{ t.trek_name }}</strong></td>
                    <td>{{ t.location }}</td>
                    <td>{{ t.difficulty }}</td>
                    <td>{{ t.duration }}d</td>
                    <td><strong>{{ t.available_slots }}</strong></td>
                    <td>{{ t.start_date }} to {{ t.end_date }}</td>
                    <td>
                      <button
                        v-if="t.available_slots > 0"
                        @click="bookTrek(t.id)"
                        class="btn btn-success btn-sm"
                        :disabled="bookingTrekId === t.id"
                      >
                        <span v-if="bookingTrekId === t.id" class="spinner-border spinner-border-sm me-1"></span>
                        {{ bookingTrekId === t.id ? 'Booking...' : 'Book' }}
                      </button>
                      <span v-else class="text-danger small fw-bold">Full</span>
                    </td>
                  </tr>
                  <tr v-if="openTreks.length === 0">
                    <td colspan="7" class="text-center text-muted">No open treks available.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 2. Search Treks (Exact search_treks.html + duration added) -->
        <div v-if="activeView === 'search_treks'" class="card shadow bg-white bg-opacity-75 mb-4">
          <div class="card-body">
            <h3 class="text-success text-center mb-3">Search Treks</h3>
            <hr />
            <div class="row g-3 mb-3">
              <div class="col-md-4">
                <label class="form-label">Location</label>
                <input v-model="searchFilter.location" type="text" class="form-control" placeholder="Location..." />
              </div>
              <div class="col-md-4">
                <label class="form-label">Difficulty</label>
                <select v-model="searchFilter.difficulty" class="form-select">
                  <option value="">Any Difficulty</option>
                  <option value="Easy">Easy</option>
                  <option value="Moderate">Moderate</option>
                  <option value="Hard">Hard</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">Max Duration (Days)</label>
                <input v-model="searchFilter.duration" type="number" min="1" class="form-control" placeholder="Max days" />
              </div>
            </div>
            <div class="text-center mb-4">
              <button @click="executeSearch" class="btn btn-success me-2" :disabled="searchLoading">
                <span v-if="searchLoading" class="spinner-border spinner-border-sm me-1"></span>
                {{ searchLoading ? 'Searching...' : 'Search' }}
              </button>
              <button @click="resetSearch" class="btn btn-secondary">Reset</button>
            </div>

            <div v-if="searchResultsList !== null">
              <h4 class="text-success">Search Results</h4>
              <table class="table table-bordered table-striped">
                <thead class="table-success">
                  <tr><th>Name</th><th>Location</th><th>Difficulty</th><th>Duration</th><th>Action</th></tr>
                </thead>
                <tbody>
                  <tr v-for="t in searchResultsList" :key="t.id">
                    <td>{{ t.trek_name }}</td><td>{{ t.location }}</td><td>{{ t.difficulty }}</td><td>{{ t.duration }}d</td>
                    <td>
                      <button
                        v-if="t.available_slots > 0"
                        @click="bookTrek(t.id)"
                        class="btn btn-success btn-sm"
                        :disabled="bookingTrekId === t.id"
                      >
                        <span v-if="bookingTrekId === t.id" class="spinner-border spinner-border-sm me-1"></span>
                        {{ bookingTrekId === t.id ? 'Booking...' : 'Book' }}
                      </button>
                      <span v-else class="text-danger small">Full</span>
                    </td>
                  </tr>
                  <tr v-if="searchResultsList.length === 0">
                    <td colspan="5" class="text-center text-muted">No treks match your search.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 3. My Bookings (my_bookings.html) -->
        <div v-if="activeView === 'my_bookings'" class="card shadow bg-white bg-opacity-75 mb-4">
          <div class="card-body">
            <h3 class="text-success text-center mb-3">My Bookings</h3>
            <div class="table-responsive">
              <table class="table table-bordered table-striped table-hover align-middle">
                <thead class="table-success">
                  <tr>
                    <th>Booking ID</th>
                    <th>Trek Name</th>
                    <th>Location</th>
                    <th>Dates</th>
                    <th>Booking Date</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="b in activeBookings" :key="b.id">
                    <td>#{{ b.id }}</td>
                    <td><strong>{{ b.trek_name }}</strong></td>
                    <td>{{ b.trek_location }}</td>
                    <td>{{ b.trek_start_date }} to {{ b.trek_end_date }}</td>
                    <td>{{ b.booking_date }}</td>
                    <td><span class="badge bg-success">{{ b.status }}</span></td>
                    <td>
                      <button @click="cancelBooking(b.id)" class="btn btn-danger btn-sm">
                        Cancel
                      </button>
                    </td>
                  </tr>
                  <tr v-if="activeBookings.length === 0">
                    <td colspan="7" class="text-center text-muted">You have no active bookings.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 4. Trekking History (trek_history.html) -->
        <div v-if="activeView === 'trekking_history'" class="card shadow bg-white bg-opacity-75 mb-4">
          <div class="card-body">
            <h3 class="text-success text-center mb-3">Trekking History</h3>
            <div class="table-responsive">
              <table class="table table-bordered table-striped table-hover align-middle">
                <thead class="table-success">
                  <tr>
                    <th>Trek Name</th>
                    <th>Location</th>
                    <th>Difficulty</th>
                    <th>Conducted Dates</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="h in historyTreks" :key="h.id">
                    <td><strong>{{ h.trek_name }}</strong></td>
                    <td>{{ h.trek_location }}</td>
                    <td>{{ h.trek_difficulty }}</td>
                    <td>{{ h.trek_start_date }} to {{ h.trek_end_date }}</td>
                    <td><span class="badge bg-primary">Completed</span></td>
                  </tr>
                  <tr v-if="historyTreks.length === 0">
                    <td colspan="5" class="text-center text-muted">No completed trek records found.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const authStore = useAuthStore()
const router = useRouter()

const activeView = ref('my_bookings')
const openTreks = ref([])
const bookings = ref([])
const historyTreks = ref([])

const searchFilter = reactive({
  location: '',
  difficulty: '',
  duration: ''
})
const searchResultsList = ref(null)
const searchLoading = ref(false)
const bookingTrekId = ref(null)

const exportLoading = ref(false)
const downloadUrl = ref(null)

const activeBookings = computed(() => {
  return bookings.value.filter(b => b.status === 'Booked')
})

async function fetchOpenTreks() {
  try {
    const res = await axios.get('/api/treks?status=Open')
    openTreks.value = res.data
  } catch (err) {
    console.error(err)
  }
}

async function fetchBookings() {
  try {
    const [bRes, hRes] = await Promise.all([
      axios.get('/api/bookings/my'),
      axios.get('/api/bookings/history')
    ])
    bookings.value = bRes.data
    historyTreks.value = hRes.data
  } catch (err) {
    console.error(err)
  }
}

async function bookTrek(trekId) {
  bookingTrekId.value = trekId
  try {
    const res = await axios.post('/api/bookings', { trek_id: trekId })
    authStore.setMessage(res.data.message || 'Trek booked successfully!', 'success')
    await Promise.all([fetchOpenTreks(), fetchBookings()])
    activeView.value = 'my_bookings'
  } catch (err) {
    authStore.setMessage(err.response?.data?.error || 'Booking failed', 'danger')
  } finally {
    bookingTrekId.value = null
  }
}

async function cancelBooking(id) {
  if (!confirm('Are you sure you want to cancel this booking?')) return
  try {
    const res = await axios.put(`/api/bookings/${id}/cancel`)
    authStore.setMessage(res.data.message || 'Booking cancelled', 'success')
    await Promise.all([fetchOpenTreks(), fetchBookings()])
  } catch (err) {
    authStore.setMessage(err.response?.data?.error || 'Cancellation failed', 'danger')
  }
}

async function executeSearch() {
  searchLoading.value = true
  try {
    const params = { status: 'Open' }
    if (searchFilter.location) params.location = searchFilter.location
    if (searchFilter.difficulty) params.difficulty = searchFilter.difficulty
    if (searchFilter.duration) params.duration = searchFilter.duration

    const res = await axios.get('/api/treks', { params })
    searchResultsList.value = res.data
  } catch (err) {
    authStore.setMessage('Search failed', 'danger')
  } finally {
    searchLoading.value = false
  }
}

function resetSearch() {
  searchFilter.location = ''
  searchFilter.difficulty = ''
  searchFilter.duration = ''
  searchResultsList.value = null
}

async function triggerExportCsv() {
  exportLoading.value = true
  try {
    const res = await axios.post('/api/bookings/export-csv')
    if (res.data.task_id) {
      authStore.setMessage('Celery batch job triggered in background...', 'info')
      pollExportStatus(res.data.task_id)
    }
  } catch (err) {
    authStore.setMessage('Failed to trigger export', 'danger')
    exportLoading.value = false
  }
}

function pollExportStatus(taskId) {
  const interval = setInterval(async () => {
    try {
      const res = await axios.get(`/api/bookings/export-status/${taskId}`)
      if (res.data.ready) {
        clearInterval(interval)
        exportLoading.value = false
        downloadUrl.value = res.data.download_url
        authStore.setMessage('CSV Batch job finished: ready for download', 'success')
      }
    } catch (e) {
      clearInterval(interval)
      exportLoading.value = false
    }
  }, 2000)
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  fetchOpenTreks()
  fetchBookings()
})
</script>
