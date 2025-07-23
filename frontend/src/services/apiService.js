import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:5000/api', 
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to request headers
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token'); 
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default {
  // == Authentication ==
  login(credentials) {
    return apiClient.post('/auth/login', credentials);
  },
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userType');
    localStorage.removeItem('student_id'); // Also clear student_id on logout
  },
  registerStudent(studentData) {
    return apiClient.post('/student/register', studentData);
  },

  // == Admin Section ==
  getAdminDashboard() {
    return apiClient.get('/admin/dashboard');
  },
  getStudents(studentId) {
    if (studentId) {
      return apiClient.get(`/admin/students?student_id=${studentId}`);
    } else {
      return apiClient.get('/admin/students');
    }
  },
  deleteStudent(studentId) {
    return apiClient.delete(`/admin/students?student_id=${studentId}`);
  },
  getSubjects(){
    return apiClient.get('/admin/subjects');
  },
  createSubject(subjectData) {
    return apiClient.post('/admin/subjects', subjectData);
  },
  updateSubject(subjectId, subjectData) {
    return apiClient.put(`/admin/subjects/${subjectId}`, subjectData);
  },
  deleteSubject(subjectId) {
    return apiClient.delete(`/admin/subjects/${subjectId}`);
  },
  getChapters(subjectId) {
    return apiClient.get(`/admin/subjects/${subjectId}/chapters`);
  },
  createChapter(subjectId, chapterData) {
    return apiClient.post(`/admin/subjects/${subjectId}/chapters`, chapterData);
  },
  updateChapter(chapterId, chapterData) {
    return apiClient.put(`/admin/chapters/${chapterId}`, chapterData);
  },
  deleteChapter(chapterId) {
    return apiClient.delete(`/admin/chapters/${chapterId}`);
  },
  getExams(chapterId) {
    if (chapterId) {
      return apiClient.get(`/admin/exams?chapter_id=${chapterId}`);
    } else {
      return apiClient.get('/admin/exams');
    }
  },
  createExam(chapterId, examData) {
    return apiClient.post(`/admin/exams?chapter_id=${chapterId}`, examData);
  },
  updateExam(examId, examData) {
    return apiClient.put(`/admin/exams/${examId}`, examData);
  },
  deleteExam(examId) {
    return apiClient.delete(`/admin/exams/${examId}`);
  },
  getQuestions(examId) {
    return apiClient.get(`/admin/exams/${examId}/questions`);
  },
  createQuestion(examId, questionData) {
    return apiClient.post(`/admin/exams/${examId}/questions`, questionData);
  },
  updateQuestion(questionId, questionData) {
    return apiClient.put(`/admin/questions/${questionId}`, questionData);
  },
  deleteQuestion(questionId) {
    return apiClient.delete(`/admin/questions/${questionId}`);
  },

  // == Student Section ==
  getStudentDashboard() {
    const studentId = localStorage.getItem('student_id');
    if (!studentId) {
      return Promise.reject(new Error('Student ID not found. Please log in again.'));
    }
    return apiClient.get(`/student/${studentId}/dashboard`);
  },
  getStudentSubjects() {
    return apiClient.get('/student/subjects');
  },
  getStudentChapters(subjectId) {
    if (subjectId) {
        return apiClient.get(`/student/chapters?subject_id=${subjectId}`);
    }
    return apiClient.get('/student/chapters');
  },
  getStudentExams({ subjectId, chapterId }) {
    let url = '/student/exams';
    if (subjectId) {
      url += `?subject_id=${subjectId}`;
    } else if (chapterId) {
      url += `?chapter_id=${chapterId}`;
    }
    return apiClient.get(url);
  },
  getStudentHistory() {
    const studentId = localStorage.getItem('student_id');
     if (!studentId) {
      return Promise.reject(new Error('Student ID not found. Please log in again.'));
    }
    return apiClient.get(`/student/${studentId}/history`);
  },
  startExam(examId) {
    const studentId = localStorage.getItem('student_id');
    if (!studentId) {
      return Promise.reject(new Error('Student ID not found. Please log in again.'));
    }
    return apiClient.post(`/student/${studentId}/exam/${examId}/start`);
  },
  submitExam(attemptId, answers) {
    const studentId = localStorage.getItem('student_id');
    if (!studentId) {
      return Promise.reject(new Error('Student ID not found. Please log in again.'));
    }
    return apiClient.post(`/student/${studentId}/attempt/${attemptId}/submit`, { answers });
  },
  getExamResults(attemptId) {
    const studentId = localStorage.getItem('student_id');
     if (!studentId) {
      return Promise.reject(new Error('Student ID not found. Please log in again.'));
    }
    return apiClient.get(`/student/${studentId}/attempt/${attemptId}/results`);
  },
};
