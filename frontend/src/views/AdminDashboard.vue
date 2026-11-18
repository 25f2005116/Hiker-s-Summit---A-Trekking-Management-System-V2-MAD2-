<template>
  <div class="container mt-5">
    <h1 class="text-center text-success mb-4">
      Welcome {{ authStore.user?.username || 'Admin' }}
    </h1>

    <div class="row">
      <!-- Left Side (Exact MAD-1 Admin_dash.html Sidebar) -->
      <div class="col-md-4 mb-4">
        <div class="card shadow bg-white bg-opacity-75">
          <div class="card-body">
            <h3 class="text-success text-center">
              What do you want to do?
            </h3>
            <hr />

            <div class="d-grid gap-2">
              <button
                @click="openCreateTrek"
                :class="['btn', activeView === 'create_trek' ? 'btn-dark' : 'btn-success']"
              >
                Create Trek
              </button>

              <button
                @click="activeView = 'view_treks'"
                :class="['btn', activeView === 'view_treks' ? 'btn-dark' : 'btn-success']"
              >
                View Treks
              </button>

              <!-- MAD-2 required addition: Admin creates staff -->
              <button
                @click="activeView = 'create_staff'"
                :class="['btn', activeView === 'create_staff' ? 'btn-dark' : 'btn-success']"
              >
                Add Staff Member
              </button>

              <button
                @click="activeView = 'view_staff'"
                :class="['btn', activeView === 'view_staff' ? 'btn-dark' : 'btn-success']"
              >
                View Staff
              </button>

              <button
                @click="activeView = 'view_users'"
                :class="['btn', activeView === 'view_users' ? 'btn-dark' : 'btn-success']"
              >
                View Users
              </button>

              <button
                @click="activeView = 'view_bookings'"
                :class="['btn', activeView === 'view_bookings' ? 'btn-dark' : 'btn-success']"
              >
                View Bookings
              </button>

              <button
                @click="activeView = 'search'"
                :class="['btn', activeView === 'search' ? 'btn-dark' : 'btn-success']"
              >
                Search
              </button>

              <button @click="handleLogout" class="btn btn-danger">
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side (Statistics + Content View) -->
      <div class="col-md-8">
        <!-- 1. Statistics Card (from Admin_dash.html) -->
        <div class="card shadow bg-white bg-opacity-75 mb-4">
          <div class="card-body">
            <h3 class="text-success text-center">
              Statistics
            </h3>
            <hr />

            <div class="row text-center">
              <div class="col-md-4 mb-3">
                <div class="card">
                  <div class="card-body">
                    <h5>Total Treks</h5>
                    <h2 class="text-success">{{ stats.total_treks || 0 }}</h2>
                  </div>
                </div>
              </div>

              <div class="col-md-4 mb-3">
                <div class="card">
                  <div class="card-body">
                    <h5>Total Users & Staff</h5>
                    <h2 class="text-success">
                      {{ (stats.total_users || 0) + (stats.total_staff || 0) }}
                    </h2>
                  </div>
                </div>
              </div>

              <div class="col-md-4 mb-3">
                <div class="card">
                  <div class="card-body">
                    <h5>Total Bookings</h5>
                    <h2 class="text-success">{{ stats.total_bookings || 0 }}</h2>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. Dynamic Content: Create / Edit Trek (create_trek.html) -->
        <div v-if="activeView === 'create_trek'" class="card shadow bg-white bg-opacity-75 mb-4">
          <div class="card-body">
            <h3 class="text-success text-center mb-3">
              {{ isEditingTrek ? 'Edit Trek' : 'Create Trek' }}
            </h3>
            <hr />

            <form @submit.prevent="saveTrek">
              <div class="mb-3">
                <label class="form-label">Trek Name</label>
                <input v-model="trekForm.trek_name" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Location</label>
                <input v-model="trekForm.location" type="text" class="form-control" required />
              </div>
              <div class="row mb-3">
                <div class="col-md-4">
                  <label class="form-label">Difficulty</label>
                  <select v-model="trekForm.difficulty" class="form-select" required>
                    <option value="Easy">Easy</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Hard">Hard</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Duration (Days)</label>
                  <input v-model="trekForm.duration" type="number" min="1" class="form-control" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Available Slots</label>
                  <input v-model="trekForm.available_slots" type="number" min="1" class="form-control" required />
                </div>
              </div>
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Start Date</label>
                  <input v-model="trekForm.start_date" type="date" class="form-control" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label">End Date</label>
                  <input v-model="trekForm.end_date" type="date" class="form-control" required />
                </div>
              </div>
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Assign Staff</label>
                  <select v-model="trekForm.assigned_staff_id" class="form-select">
                    <option :value="null">Unassigned</option>
                    <option v-for="s in staffList" :key="s.id" :value="s.id">{{ s.username }}</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Status</label>
                  <select v-model="trekForm.status" class="form-select">
                    <option value="Open">Open</option>
                    <option value="Closed">Closed</option>
                    <option value="Started">Started</option>
                    <option value="Completed">Completed</option>
                  </select>
                </div>
              </div>

              <div class="text-center mt-4">
                <button type="submit" class="btn btn-success me-2">
                  {{ isEditingTrek ? 'Update Trek' : 'Save Trek' }}
                </button>
                <button type="button" @click="activeView = 'view_treks'" class="btn btn-secondary">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- 3. Dynamic Content: View Treks Table (view_trek.html) -->
        <div v-if="activeView === 'view_treks'" class="card shadow bg-white bg-opacity-75 mb-4">
          <div class="card-body">
            <h3 class="text-success text-center mb-3">All Treks</h3>
            <div class="table-responsive">
              <table class="table table-bordered table-striped table-hover align-middle">
                <thead class="table-success">
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Location</th>
                    <th>Difficulty</th>
                    <th>Duration</th>
                    <th>Available Slots</th>
                    <th>Staff</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="t in allTreks" :key="t.id">
                    <td>{{ t.id }}</td>
                    <td><strong>{{ t.trek_name }}</strong></td>
                    <td>{{ t.location }}</td>
                    <td>{{ t.difficulty }}</td>
                    <td>{{ t.duration }}d</td>
                    <td><strong>{{ t.available_slots }}</strong></td>
                    <td>
                      <select
                        class="form-select form-select-sm"
                        :value="t.assigned_staff_id || ''"
                        @change="handleAssignStaff(t.id, $event.target.value)"
                      >
                        <option value="">None</option>
                        <option v-for="s in staffList" :key="s.id" :value="s.id">{{ s.username }}</option>
                      </select>
                    </td>
                    <td><span class="badge bg-success">{{ t.status }}</span></td>
                    <td>
                      <button @click="openEditTrek(t)" class="btn btn-sm btn-primary me-1">Edit</button>
                      <button @click="deleteTrek(t.id)" class="btn btn-sm btn-danger">Delete</button>
                    </td>
                  </tr>
                  <tr v-if="allTreks.length === 0">
                    <td colspan="9" class="text-center text-muted">No treks created yet.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 4. Dynamic Content: Create Staff (MAD-2 requirement) -->
        <div v-if="activeView === 'create_staff'" class="card shadow bg-white bg-opacity-75 mb-4">
          <div class="card-body">
            <h3 class="text-success text-center mb-3">Add New Trek Staff</h3>
            <hr />
            <form @submit.prevent="createStaff">
              <div class="mb-3">
                <label class="form-label">Staff Username</label>
                <input v-model="staffForm.username" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Contact Details (Email or Phone)</label>
                <input v-model="staffForm.contact_details" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input v-model="staffForm.password" type="password" class="form-control" required />
              </div>
              <div class="text-center">
                <button type="submit" class="btn btn-success me-2">Create Staff</button>
                <button type="button" @click="activeView = 'view_staff'" class="btn btn-secondary">Cancel</button>
              </div>
            </form>
          </div>
        </div>

        <!-- 5. Dynamic Content: View Staff Table (view_staff.html) -->
        <div v-if="activeView === 'view_staff'" class="card shadow bg-white bg-opacity-75 mb-4">
          <div class="card-body">
            <h3 class="text-success text-center mb-3">Trek Staff</h3>
            <div class="table-responsive">
              <table class="table table-bordered table-striped table-hover align-middle">
                <thead class="table-success">
                  <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Contact</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="s in staffList" :key="s.id">
                    <td>{{ s.id }}</td>
                    <td><strong>{{ s.username }}</strong></td>
                    <td>{{ s.contact_details || 'N/A' }}</td>
                    <td><span class="badge" :class="s.status === 'Approved' ? 'bg-success' : 'bg-danger'">{{ s.status }}</span></td>
                    <td>
                      <button
                        @click="toggleUserStatus(s.id)"
                        :class="['btn btn-sm', s.status === 'Approved' ? 'btn-danger' : 'btn-success']"
                      >
                        {{ s.status === 'Approved' ? 'Blacklist' : 'Approve' }}
                      </button>
                    </td>
                  </tr>
                  <tr v-if="staffList.length === 0">
                    <td colspan="5" class="text-center text-muted">No staff members found.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 6. Dynamic Content: View Users Table (view_users.html) -->
        <div v-if="activeView === 'view_users'" class="card shadow bg-white bg-opacity-75 mb-4">
          <div class="card-body">
            <h3 class="text-success text-center mb-3">Registered Users</h3>
            <div class="table-responsive">
              <table class="table table-bordered table-striped table-hover align-middle">
                <thead class="table-success">
                  <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Contact</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="u in userList" :key="u.id">
                    <td>{{ u.id }}</td>
                    <td><strong>{{ u.username }}</strong></td>
                    <td>{{ u.contact_details || 'N/A' }}</td>
                    <td><span class="badge" :class="u.status === 'Approved' ? 'bg-success' : 'bg-danger'">{{ u.status }}</span></td>
                    <td>
                      <button
                        @click="toggleUserStatus(u.id)"
                        :class="['btn btn-sm', u.status === 'Approved' ? 'btn-danger' : 'btn-success']"
                      >
                        {{ u.status === 'Approved' ? 'Blacklist' : 'Whitelist' }}
                      </button>
                    </td>
                  </tr>
                  <tr v-if="userList.length === 0">
                    <td colspan="5" class="text-center text-muted">No users registered yet.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 7. Dynamic Content: View Bookings Table (view_bookings.html) -->
        <div v-if="activeView === 'view_bookings'" class="card shadow bg-white bg-opacity-75 mb-4">
          <div class="card-body">
            <h3 class="text-success text-center mb-3">All Bookings</h3>
            <div class="table-responsive">
              <table class="table table-bordered table-striped table-hover align-middle">
                <thead class="table-success">
                  <tr>
                    <th>ID</th>
                    <th>User</th>
                    <th>Trek</th>
                    <th>Location</th>
                    <th>Date</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="b in allBookings" :key="b.id">
                    <td>#{{ b.id }}</td>
                    <td>{{ b.username }}</td>
                    <td><strong>{{ b.trek_name }}</strong></td>
                    <td>{{ b.trek_location }}</td>
                    <td>{{ b.booking_date }}</td>
                    <td><span class="badge bg-success">{{ b.status }}</span></td>
                  </tr>
                  <tr v-if="allBookings.length === 0">
                    <td colspan="6" class="text-center text-muted">No bookings placed yet.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 8. Dynamic Content: Search (search.html & search_results.html) -->
        <div v-if="activeView === 'search'" class="card shadow bg-white bg-opacity-75 mb-4">
          <div class="card-body">
            <h3 class="text-success text-center mb-3">Search System</h3>
            <div class="input-group mb-4">
              <input
                v-model="searchQuery"
                @keyup.enter="handleSearch"
                type="text"
                class="form-control"
                placeholder="Search by ID or name..."
              />
              <button @click="handleSearch" class="btn btn-success">Search</button>
            </div>

            <div v-if="searchResults">
              <h5 class="text-success">Matching Treks</h5>
              <table class="table table-bordered mb-3">
                <thead class="table-success">
                  <tr><th>ID</th><th>Name</th><th>Location</th></tr>
                </thead>
                <tbody>
                  <tr v-for="t in searchResults.treks" :key="t.id">
                    <td>{{ t.id }}</td><td>{{ t.trek_name }}</td><td>{{ t.location }}</td>
                  </tr>
                </tbody>
              </table>

              <h5 class="text-success">Matching Users</h5>
              <table class="table table-bordered mb-3">
                <thead class="table-success">
                  <tr><th>ID</th><th>Username</th><th>Status</th></tr>
                </thead>
                <tbody>
                  <tr v-for="u in searchResults.users" :key="u.id">
                    <td>{{ u.id }}</td><td>{{ u.username }}</td><td>{{ u.status }}</td>
                  </tr>
                </tbody>
              </table>

              <h5 class="text-success">Matching Staff</h5>
              <table class="table table-bordered">
                <thead class="table-success">
                  <tr><th>ID</th><th>Username</th><th>Status</th></tr>
                </thead>
                <tbody>
                  <tr v-for="s in searchResults.staff" :key="s.id">
                    <td>{{ s.id }}</td><td>{{ s.username }}</td><td>{{ s.status }}</td>
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
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const authStore = useAuthStore()
const router = useRouter()

const activeView = ref('view_treks')
const stats = ref({})
const allTreks = ref([])
const staffList = ref([])
const userList = ref([])
const allBookings = ref([])

const searchQuery = ref('')
const searchResults = ref(null)

const isEditingTrek = ref(false)
const editingTrekId = ref(null)
const trekForm = reactive({
  trek_name: '',
  location: '',
  difficulty: 'Moderate',
  duration: null,
  available_slots: null,
  start_date: '',
  end_date: '',
  assigned_staff_id: null,
  status: 'Open'
})

const staffForm = reactive({
  username: '',
  password: '',
  contact_details: ''
})

async function fetchStats() {
  try {
    const res = await axios.get('/api/admin/dashboard-stats')
    stats.value = res.data
  } catch (err) {
    console.error(err)
  }
}

async function fetchTreks() {
  const res = await axios.get('/api/treks/all')
  allTreks.value = res.data
}

async function fetchStaff() {
  const res = await axios.get('/api/admin/staff')
  staffList.value = res.data
}

async function fetchUsers() {
  const res = await axios.get('/api/admin/users')
  userList.value = res.data
}

async function fetchBookings() {
  const res = await axios.get('/api/admin/bookings')
  allBookings.value = res.data
}

async function refreshAll() {
  await Promise.all([
    fetchStats(),
    fetchTreks(),
    fetchStaff(),
    fetchUsers(),
    fetchBookings()
  ])
}

function openCreateTrek() {
  isEditingTrek.value = false
  editingTrekId.value = null
  Object.assign(trekForm, {
    trek_name: '',
    location: '',
    difficulty: 'Moderate',
    duration: null,
    available_slots: null,
    start_date: '',
    end_date: '',
    assigned_staff_id: null,
    status: 'Open'
  })
  activeView.value = 'create_trek'
}

function openEditTrek(t) {
  isEditingTrek.value = true
  editingTrekId.value = t.id
  Object.assign(trekForm, {
    trek_name: t.trek_name,
    location: t.location,
    difficulty: t.difficulty,
    duration: t.duration,
    available_slots: t.available_slots,
    start_date: t.start_date,
    end_date: t.end_date,
    assigned_staff_id: t.assigned_staff_id,
    status: t.status
  })
  activeView.value = 'create_trek'
}

async function saveTrek() {
  try {
    if (isEditingTrek.value) {
      await axios.put(`/api/treks/${editingTrekId.value}`, trekForm)
      authStore.setMessage('Trek updated successfully', 'success')
    } else {
      await axios.post('/api/treks', trekForm)
      authStore.setMessage('Trek created successfully', 'success')
    }
    activeView.value = 'view_treks'
    await refreshAll()
  } catch (err) {
    authStore.setMessage(err.response?.data?.error || 'Failed to save trek', 'danger')
  }
}

async function deleteTrek(id) {
  if (!confirm('Are you sure you want to delete this trek?')) return
  try {
    await axios.delete(`/api/treks/${id}`)
    authStore.setMessage('Trek deleted', 'success')
    await refreshAll()
  } catch (err) {
    authStore.setMessage('Failed to delete trek', 'danger')
  }
}

async function handleAssignStaff(trekId, staffId) {
  try {
    await axios.put(`/api/admin/treks/${trekId}/assign-staff`, {
      staff_id: staffId ? parseInt(staffId) : null
    })
    authStore.setMessage('Staff assigned to trek', 'success')
    await fetchTreks()
  } catch (err) {
    authStore.setMessage('Failed to assign staff', 'danger')
  }
}

async function createStaff() {
  try {
    await axios.post('/api/admin/staff', staffForm)
    authStore.setMessage('Staff account created', 'success')
    staffForm.username = ''
    staffForm.password = ''
    staffForm.contact_details = ''
    activeView.value = 'view_staff'
    await fetchStaff()
  } catch (err) {
    authStore.setMessage(err.response?.data?.error || 'Failed to create staff', 'danger')
  }
}

async function toggleUserStatus(userId) {
  try {
    const res = await axios.put(`/api/admin/users/${userId}/toggle-status`)
    authStore.setMessage(res.data.message, 'success')
    await Promise.all([fetchUsers(), fetchStaff()])
  } catch (err) {
    authStore.setMessage('Failed to update status', 'danger')
  }
}

async function handleSearch() {
  if (!searchQuery.value.trim()) return
  try {
    const res = await axios.get('/api/admin/search', { params: { q: searchQuery.value } })
    searchResults.value = res.data
  } catch (err) {
    authStore.setMessage('Search failed', 'danger')
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  refreshAll()
})
</script>
