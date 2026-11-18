import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import StaffDashboard from '../views/StaffDashboard.vue'
import UserDashboard from '../views/UserDashboard.vue'
import ProfileView from '../views/ProfileView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'Admin' }
  },
  {
    path: '/staff',
    name: 'StaffDashboard',
    component: StaffDashboard,
    meta: { requiresAuth: true, role: 'Staff' }
  },
  {
    path: '/dashboard',
    name: 'UserDashboard',
    component: UserDashboard,
    meta: { requiresAuth: true, role: 'User' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
    if (authStore.isAdmin) return next({ name: 'AdminDashboard' })
    if (authStore.isStaff) return next({ name: 'StaffDashboard' })
    if (authStore.isUser) return next({ name: 'UserDashboard' })
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    authStore.setMessage('Please log in to access this page.', 'warning')
    return next({ name: 'Login' })
  }

  if (to.meta.role && authStore.role !== to.meta.role) {
    authStore.setMessage('Access Denied: Unauthorized role.', 'danger')
    if (authStore.isAdmin) return next({ name: 'AdminDashboard' })
    if (authStore.isStaff) return next({ name: 'StaffDashboard' })
    if (authStore.isUser) return next({ name: 'UserDashboard' })
    return next({ name: 'Home' })
  }

  next()
})

export default router
