import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';

// Admin Views
import AdminLayout from '../components/AdminLayout.vue'; // The layout is now a route component
import AdminDashboard from '../views/admin/AdminDashboard.vue';
import Subjects from '../views/admin/Subjects.vue';
import Chapters from '../views/admin/Chapters.vue';
import AdminExams from '../views/admin/AdminExams.vue';
import Questions from '../views/admin/Questions.vue';
import Students from '../views/admin/Students.vue';

// Student Views
import StudentDashboard from '../views/student/Dashboard.vue';
import StudentExams from '../views/student/Exams.vue';
import StudentHistory from '../views/student/History.vue';
import Quiz from '../views/student/Quiz.vue';
import Results from '../views/student/Results.vue';
import StudentProfile from '../views/student/Profile.vue';

import ApiLoading from '../views/ApiLoading.vue';

const routes = [
    {
        path: '/',
        name: 'ApiLoading',
        component: ApiLoading,
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { requiresGuest: true }
    },
    {
        path: '/register',
        name: 'Register',
        component: Register,
        meta: { requiresGuest: true }
    },

    // Admin Routes
    {
        path: '/admin',
        component: AdminLayout,
        meta: { requiresAuth: true, role: 'admin' },
        children: [
            {
                path: 'dashboard',
                name: 'AdminDashboard',
                component: AdminDashboard,
            },
            {
                path: 'subjects',
                name: 'Subjects',
                component: Subjects,
            },
            {
                path: 'subjects/:subjectId/chapters',
                name: 'Chapters',
                component: Chapters,
                props: true,
            },
            {
                path: 'exams',
                name: 'AdminExams',
                component: AdminExams,
                props: route => ({ chapterId: route.query.chapterId }),
            },
            {
                path: 'exam/:examId/questions',
                name: 'Questions',
                component: Questions,
                props: true,
            },
            {
                path: 'students',
                name: 'AdminUsers',
                component: Students,
            }
        ]
    },

    // --- Student Routes ---
    {
        path: '/student/dashboard',
        name: 'StudentDashboard',
        component: StudentDashboard,
        meta: { requiresAuth: true, role: 'student' }
    },
    {
        path: '/student/exams',
        name: 'StudentExams',
        component: StudentExams,
        meta: { requiresAuth: true, role: 'student' }
    },
    {
        path: '/student/history',
        name: 'StudentHistory',
        component: StudentHistory,
        meta: { requiresAuth: true, role: 'student' }
    },
    {
        path: '/student/exam/:examId/attempt',
        name: 'StudentQuiz',
        component: Quiz,
        props: true,
        meta: { requiresAuth: true, role: 'student' }
    },
    {
        path: '/student/attempt/:attemptId/results',
        name: 'StudentResults',
        component: Results,
        props: true,
        meta: { requiresAuth: true, role: 'student' }
    },
    {
        path: '/student/profile',
        name: 'StudentProfile',
        component: StudentProfile,
        meta: { requiresAuth: true, role: 'student' }
    },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// Navigation Guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const userType = localStorage.getItem('userType');
  const requiredRole = to.matched.find(record => record.meta.role)?.meta.role;

  if (requiredRole) {
    if (token && userType === requiredRole) {
      next();
    } else {
      localStorage.clear();
      next('/login');
    }
  } else if (to.meta.requiresGuest && token) {
    if (userType === 'admin') {
      next('/admin/dashboard');
    } else {
      next('/student/dashboard');
    }
  } else {
    next();
  }
});

export default router;
