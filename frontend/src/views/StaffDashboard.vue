<template>
  <div class="container mt-5">
    <!-- Header -->
    <h1 class="text-center text-success mb-4">
      Welcome {{ authStore.user?.username }}
    </h1>

    <!-- Direct Assigned Treks Table (No redundant "What do you want to do" card) -->
    <div class="row justify-content-center">
      <div class="col-md-11">
        <div class="card shadow bg-white bg-opacity-75 mb-4">
          <div class="card-body">
            <h3 class="text-success text-center mb-3">Assigned Treks</h3>
            
            <div class="table-responsive">
              <table class="table table-bordered table-striped table-hover align-middle">
                <thead class="table-success">
                  <tr>
                    <th>Trek Name</th>
                    <th>Location</th>
                    <th>Difficulty</th>
                    <th>Duration</th>
                    <th>Available Slots</th>
                    <th>Participants</th>
                    <th>Status</th>
                    <th>Update</th>
                    <th>View Participants</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="t in assignedTreks" :key="t.id">
                    <td><strong>{{ t.trek_name }}</strong></td>
                    <td>{{ t.location }}</td>
                    <td>{{ t.difficulty }}</td>
                    <td>{{ t.duration }} Days</td>
                    <td><strong>{{ t.available_slots }}</strong></td>
                    <td><strong class="text-primary">{{ t.participant_count }}</strong></td>
                    <td><span class="badge bg-success">{{ t.status }}</span></td>
                    <td>
                      <button @click="openUpdateModal(t)" class="btn btn-success btn-sm">
                        Update
                      </button>
                    </td>
                    <td>
                      <button @click="openParticipantsModal(t)" class="btn btn-primary btn-sm">
                        Participants
                      </button>
                    </td>
                  </tr>
                  <tr v-if="assignedTreks.length === 0">
                    <td colspan="9" class="text-center text-muted py-3">No treks currently assigned to you.</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Logout button cleanly at the bottom of the table -->
            <div class="text-center mt-4">
              <button @click="handleLogout" class="btn btn-danger px-4">
                Logout
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>

    <!-- Update Trek Modal (Exact update_assigned_trek.html) -->
    <div v-if="showUpdateModal" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog">
        <div class="modal-content shadow border-0">
          <div class="modal-header bg-success text-white">
            <h5 class="modal-title">Update Assigned Trek</h5>
            <button type="button" class="btn-close btn-close-white" @click="showUpdateModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitStaffUpdate">
              <div class="mb-3">
                <label class="form-label">Available Slots</label>
                <input v-model="updateForm.available_slots" type="number" min="0" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Status</label>
                <select v-model="updateForm.status" class="form-select" required>
                  <option value="Open">Open</option>
                  <option value="Closed">Closed</option>
                  <option value="Started">Started</option>
                  <option value="Completed">Completed</option>
                </select>
              </div>
              <div class="text-center">
                <button type="submit" class="btn btn-success me-2">Save</button>
                <button type="button" class="btn btn-secondary" @click="showUpdateModal = false">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- View Participants Modal (view_participants.html) -->
    <div v-if="showParticipantsModal" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-lg">
        <div class="modal-content shadow border-0">
          <div class="modal-header bg-success text-white">
            <h5 class="modal-title">Participants: {{ selectedTrek?.trek_name }}</h5>
            <button type="button" class="btn-close btn-close-white" @click="showParticipantsModal = false"></button>
          </div>
          <div class="modal-body">
            <table class="table table-bordered table-striped" v-if="participantsList.length > 0">
              <thead class="table-success">
                <tr><th>#</th><th>User</th><th>Contact</th><th>Booking Date</th></tr>
              </thead>
              <tbody>
                <tr v-for="(p, i) in participantsList" :key="p.booking_id">
                  <td>{{ i + 1 }}</td>
                  <td><strong>{{ p.username }}</strong></td>
                  <td>{{ p.contact_details || 'N/A' }}</td>
                  <td>{{ p.booking_date }}</td>
                </tr>
              </tbody>
            </table>
            <p v-else class="text-center text-muted mb-0">No participants booked yet.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showParticipantsModal = false">Close</button>
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

const assignedTreks = ref([])

const showUpdateModal = ref(false)
const selectedTrek = ref(null)
const updateForm = reactive({
  available_slots: 0,
  status: 'Open'
})

const showParticipantsModal = ref(false)
const participantsList = ref([])

async function fetchAssignedTreks() {
  try {
    const res = await axios.get('/api/staff/assigned-treks')
    assignedTreks.value = res.data
  } catch (err) {
    console.error(err)
  }
}

function openUpdateModal(trek) {
  selectedTrek.value = trek
  updateForm.available_slots = trek.available_slots
  updateForm.status = trek.status
  showUpdateModal.value = true
}

async function submitStaffUpdate() {
  try {
    await axios.put(`/api/treks/${selectedTrek.value.id}/staff-update`, updateForm)
    authStore.setMessage('Trek details updated', 'success')
    showUpdateModal.value = false
    await fetchAssignedTreks()
  } catch (err) {
    authStore.setMessage(err.response?.data?.error || 'Update failed', 'danger')
  }
}

async function openParticipantsModal(trek) {
  selectedTrek.value = trek
  try {
    const res = await axios.get(`/api/staff/treks/${trek.id}/participants`)
    participantsList.value = res.data.participants
    showParticipantsModal.value = true
  } catch (err) {
    authStore.setMessage('Failed to fetch participants', 'danger')
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  fetchAssignedTreks()
})
</script>
