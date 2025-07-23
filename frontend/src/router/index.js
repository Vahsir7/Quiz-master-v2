import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import AdminDashboard from '../views/admin/AdminDashboard.vue';
import Subjects from '../views/admin/Subjects.vue';
import Chapters from '../views/admin/Chapters.vue';
import Exams from '../views/admin/Exams.vue'; 
import ExamCreate from '../views/admin/Exams.vue';
import Questions from '../views/admin/Questions.vue';
import Students from '../views/admin/Students.vue';

// Define the application routes
const routes = [
    {
        path: '/',
        redirect: '/login',
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { requiresGuest: true }
    },
    {
        path: '/admin/dashboard',
        name: 'AdminDashboard',
        component: AdminDashboard,
        meta: { requiresAuth: true, role: 'admin' }
    },
    
    {
        path: '/admin/subjects',
        name: 'Subjects',
        component: Subjects,
        meta: { requiresAuth: true, role: 'admin' }
    },
    {
        path: '/admin/subjects/:subjectId/chapters',
        name: 'Chapters',
        component: Chapters,
        props: true,
        meta: { requiresAuth: true, role: 'admin' }
    },
    {
        path: '/admin/exams',
        name: 'Exams',
        component: Exams,
        props: route => ({ chapterId: route.query.chapterId }), 
        meta: { requiresAuth: true, role: 'admin' }
    },
    {
        path: '/admin/exams/new',
        name: 'ExamCreate',
        component: ExamCreate,
        meta: { requiresAuth: true, role: 'admin' }
    },
    {
        path: '/admin/exams/:examId/edit',
        name: 'ExamEdit',
        component: ExamCreate, // Reuse the same component for editing
        props: true,
        meta: { requiresAuth: true, role: 'admin' }
    },
    {
        path: '/admin/exams/:examId/questions',
        name: 'Questions',
        component: Questions,
        props: true,
        meta: { requiresAuth: true, role: 'admin' }
    },
    {
        path: '/admin/students',
        name: 'AdminStudents',
        component: Students,
        meta: { requiresAuth: true, role: 'admin' }
    },
];

// Create the router instance
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// Navigation Guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const userType = localStorage.getItem('userType');

  if (to.meta.requiresAuth) {
    if (token && userType === to.meta.role) {
      next();
    } else {
      localStorage.clear();
      next('/login');
    }
  } else if (to.meta.requiresGuest && token) {
    if (userType === 'admin') {
      next('/admin/dashboard');
    } else {
      // Assuming a student dashboard route exists
      next('/student/dashboard'); 
    }
  } else {
    next();
  }
});

export default router;
