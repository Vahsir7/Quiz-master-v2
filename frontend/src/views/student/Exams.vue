<template>
    <div class="dashboard-header">
      <h2>Browse All Exams</h2>
      <p>Find a quiz to test your knowledge.</p>
    </div>

    <div class="filter-bar">
      <div class="filter-group">
        <input
          type="text"
          v-model="filters.searchQuery"
          placeholder="Search by exam name..."
          class="search-input"
        />
      </div>
      <div class="filter-group">
        <select v-model="filters.subject" class="filter-select">
          <option value="All">All Subjects</option>
          <option v-for="subject in subjects" :key="subject.subject_id" :value="subject.subject_id">
            {{ subject.subject_name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <select v-model="filters.chapter" class="filter-select">
          <option value="All">All Chapters</option>
           <option v-for="chapter in availableChapters" :key="chapter.chapter_id" :value="chapter.chapter_id">
            {{ chapter.chapter_name }}
          </option>
        </select>
      </div>
      <div class="filter-group checkbox-group">
        <label for="past-exams">View Past Exams</label>
        <input type="checkbox" id="past-exams" v-model="filters.past" class="filter-checkbox" />
      </div>
    </div>

    <div v-if="loading" class="text-center">Loading exams...</div>
    <div v-if="error" class="error-box">{{ error }}</div>

    <div v-if="!loading" class="table-wrapper">
      <table class="data-table">
        <thead class="bg-gray-50">
          <tr>
            <th>Exam Name</th>
            <th>Total Marks</th>
            <th>Questions</th>
            <th>Duration</th>
            <th>Availability</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="exam in filteredExams" :key="exam.exam_id">
            <td class="font-medium">{{ exam.exam_name }}</td>
            <td>{{ exam.total_marks }}</td>
            <td>{{ exam.total_questions }}</td>
            <td>{{ exam.total_duration }} mins</td>
            <td>
              <div v-if="exam.exam_type === 'specific_time' && exam.start_time">
                <p class="font-semibold">{{ new Date(exam.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}</p>
                <p class="text-xs text-gray-500">{{ new Date(exam.start_time).toLocaleDateString() }}</p>
              </div>
              <div v-else>
                <p class="font-semibold">Deadline</p>
                <p class="text-xs text-gray-500">{{ new Date(exam.exam_date).toLocaleDateString() }}</p>
              </div>
            </td>
            <td>
              <button @click="openStartModal(exam)" v-if="isAttemptable(exam)" class="btn-start-quiz">Start</button>
              <span v-else class="text-red-500 font-semibold">Over</span>
            </td>
          </tr>
          <tr v-if="filteredExams.length === 0">
            <td colspan="6" class="text-center text-gray-500 py-4">No exams match your criteria.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isStartModalOpen" class="modal-overlay">
      <div class="modal-content text-center">
        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
          <i class="fas fa-play-circle text-blue-600 text-xl"></i>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mt-5">Start Exam</h3>
        <p class="text-sm text-gray-500 mt-2">Are you sure you want to begin the exam "{{ examToStart.exam_name }}"?</p>
        <div class="text-left text-sm text-gray-600 mt-4 p-3 bg-gray-50 rounded-lg">
            <p><strong>Questions:</strong> {{ examToStart.total_questions }}</p>
            <p><strong>Duration:</strong> {{ examToStart.total_duration }} minutes</p>
        </div>
        <div class="flex justify-center space-x-4 mt-6">
          <button @click="closeStartModal" class="btn btn-secondary">Cancel</button>
          <button @click="confirmStartExam" class="btn-start-quiz">Start Exam</button>
        </div>
      </div>
    </div>
</template>

<script>
import apiService from '@/services/apiService';
import StudentLayout from '@/components/StudentLayout.vue';

export default {
  name: 'StudentExams',
  components: { StudentLayout },
  data() {
    return {
      exams: [],
      subjects: [],
      chapters: [],
      loading: true,
      error: null,
      filters: {
        searchQuery: '',
        subject: 'All',
        chapter: 'All',
        past: false,
      },
      isStartModalOpen: false,
      examToStart: null,
    };
  },
  computed: {
    availableChapters() {
      if (this.filters.subject === 'All') {
        return this.chapters;
      }
      return this.chapters.filter(chapter => chapter.subject_id === this.filters.subject);
    },
    filteredExams() {
      let exams = this.exams;

      if (this.filters.searchQuery) {
        const lowerCaseSearch = this.filters.searchQuery.toLowerCase();
        exams = exams.filter(exam =>
          exam.exam_name.toLowerCase().includes(lowerCaseSearch)
        );
      }

      const chapterIdsInSubject = new Set(this.availableChapters.map(c => c.chapter_id));

      if (this.filters.subject !== 'All') {
        exams = exams.filter(exam => chapterIdsInSubject.has(exam.chapter_id));
      }

      if (this.filters.chapter !== 'All') {
        exams = exams.filter(exam => exam.chapter_id === this.filters.chapter);
      }

      const now = new Date();
      if (this.filters.past) {
        exams = exams.filter(exam => !this.isAvailable(exam, now));
      } else {
        exams = exams.filter(exam => this.isAvailable(exam, now));
      }

      return exams;
    }
  },
  watch: {
    'filters.subject'() {
      this.filters.chapter = 'All';
    }
  },
  async mounted() {
    this.fetchAllData();
  },
  methods: {
    async fetchAllData() {
      this.loading = true;
      this.error = null;
      try {
        const [examsRes, subjectsRes, chaptersRes] = await Promise.all([
          apiService.getStudentExams({}),
          apiService.getStudentSubjects(),
          apiService.getStudentChapters()
        ]);
        this.exams = examsRes.data;
        this.subjects = subjectsRes.data;
        this.chapters = chaptersRes.data;
      } catch (err) {
        this.error = 'Failed to load page data.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    isAvailable(exam, now) {
      if (exam.exam_type === 'specific_time') {
        if (!exam.start_time) return false;
        const endTime = new Date(new Date(exam.start_time).getTime() + exam.total_duration * 60000);
        return now <= endTime;
      } else { // deadline
        const deadlineDate = new Date(exam.exam_date);
        deadlineDate.setHours(23, 59, 59, 999);
        return now <= deadlineDate;
      }
    },
    isAttemptable(exam) {
      const now = new Date();
      if (exam.exam_type === 'specific_time') {
          if (!exam.start_time) return false;
          const startTime = new Date(exam.start_time);
          const endTime = new Date(startTime.getTime() + exam.total_duration * 60000);
          return now >= startTime && now <= endTime;
      } else { // 'deadline'
          const deadlineDate = new Date(exam.exam_date);
          deadlineDate.setHours(23, 59, 59, 999);
          return now <= deadlineDate;
      }
    },
    openStartModal(exam) {
      this.examToStart = exam;
      this.isStartModalOpen = true;
    },
    closeStartModal() {
      this.isStartModalOpen = false;
      this.examToStart = null;
    },
    confirmStartExam() {
      if (!this.examToStart) return;
      this.$router.push({
        name: 'StudentQuiz',
        params: { examId: this.examToStart.exam_id }
      });
    }
  }
};
</script>

<style scoped>
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem;
  background-color: #ffffff;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.filter-group {
  flex: 1 1 200px;
}
.search-input, .filter-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #bdc3c7;
  border-radius: 5px;
  font-size: 1rem;
}
.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-basis: 100%;
  flex-grow: 0;
  min-width: 150px;
}
.filter-checkbox {
  width: 1.25rem;
  height: 1.25rem;
}
.btn-start-quiz {
  background-color: #2ecc71;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-start-quiz:hover {
  background-color: #27ae60;
}
</style>
