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
  },
  registerStudent(studentData) {
    return apiClient.post('/auth/register', studentData);
  },

  // == Admin Dashboard ==
  getAdminDashboard() {
    return apiClient.get('/admin/dashboard');
  },

  // == Students ==
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
  // == Subjects ==
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

  // == Chapters ==
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

  // == Exams ==
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
  
  // == Questions ==
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
  }
};