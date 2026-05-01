<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import api from '@/lib/api';
import {
  UserCheck, UserPlus, Search, Edit, Trash2, X, Mail, Phone,
  ChevronLeft, ChevronRight, Loader2, Building2, Briefcase,
  CalendarDays, Droplets, MapPin, AlertCircle, Users,
} from '@lucide/vue';

interface Employee {
  id: string; employee_code: string; first_name: string; last_name: string;
  phone: string; email: string; designation: string; department: string;
  salary: number; join_date: string; is_active: boolean; avatar_url: string | null;
  blood_group: string; address: string; emergency_contact: string;
  emergency_phone: string; organization_id: string; created_at: string;
}
interface PaginationMeta { page: number; per_page: number; total: number; total_pages: number; }

const DEPARTMENTS = ['Engineering', 'Construction', 'Architecture', 'Accounts', 'HR', 'Management'];
const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
const emptyForm = () => ({
  first_name: '', last_name: '', phone: '', email: '', designation: '',
  department: '', salary: '' as string | number, join_date: '',
  emergency_contact: '', emergency_phone: '', address: '', blood_group: '',
});

const employees = ref<Employee[]>([]);
const loading = ref(true);
const saving = ref(false);
const searchQuery = ref('');
const deptFilter = ref('');
const currentPage = ref(1);
const perPage = ref(20);
const meta = ref<PaginationMeta>({ page: 1, per_page: 20, total: 0, total_pages: 0 });
const errorMessage = ref('');

// Modals
const showFormModal = ref(false);
const showDeleteDialog = ref(false);
const deleting = ref(false);
const isEditing = ref(false);
const selectedEmployee = ref<Employee | null>(null);

const form = reactive(emptyForm());

async function fetchEmployees() {
  loading.value = true;
  errorMessage.value = '';
  try {
    const params: Record<string, any> = { page: currentPage.value, per_page: perPage.value };
    if (deptFilter.value) params.department = deptFilter.value;
    const { data } = await api.get('/employees', { params });
    employees.value = data.data || [];
    meta.value = data.meta || { page: 1, per_page: 20, total: 0, total_pages: 0 };
  } catch {
    errorMessage.value = 'Failed to load employees. Please try again.';
  } finally { loading.value = false; }
}

async function saveEmployee() {
  if (!form.first_name.trim() || !form.last_name.trim()) return;
  saving.value = true;
  errorMessage.value = '';
  const payload = {
    first_name: form.first_name.trim(), last_name: form.last_name.trim(),
    phone: form.phone.trim() || undefined, email: form.email.trim() || undefined,
    designation: form.designation.trim() || undefined, department: form.department || undefined,
    salary: form.salary ? Number(form.salary) : undefined, join_date: form.join_date || undefined,
    emergency_contact: form.emergency_contact.trim() || undefined,
    emergency_phone: form.emergency_phone.trim() || undefined,
    address: form.address.trim() || undefined, blood_group: form.blood_group || undefined,
  };
  try {
    if (isEditing.value && selectedEmployee.value) {
      await api.put(`/employees/${selectedEmployee.value.id}`, payload);
    } else {
      await api.post('/employees', payload);
    }
    closeFormModal();
    await fetchEmployees();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error?.message || 'Failed to save employee.';
  } finally { saving.value = false; }
}

async function deleteEmployee() {
  if (!selectedEmployee.value) return;
  deleting.value = true;
  try {
    await api.delete(`/employees/${selectedEmployee.value.id}`);
    showDeleteDialog.value = false;
    selectedEmployee.value = null;
    await fetchEmployees();
  } catch {
    errorMessage.value = 'Failed to delete employee.';
  } finally { deleting.value = false; }
}

function getInitials(emp: Employee): string {
  return (emp.first_name?.charAt(0)?.toUpperCase() || '') + (emp.last_name?.charAt(0)?.toUpperCase() || '');
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function openCreateModal() {
  isEditing.value = false;
  selectedEmployee.value = null;
  Object.assign(form, emptyForm());
  errorMessage.value = '';
  showFormModal.value = true;
}

function openEditModal(emp: Employee) {
  isEditing.value = true;
  selectedEmployee.value = emp;
  Object.assign(form, {
    first_name: emp.first_name, last_name: emp.last_name, phone: emp.phone || '',
    email: emp.email || '', designation: emp.designation || '', department: emp.department || '',
    salary: emp.salary || '', join_date: emp.join_date || '',
    emergency_contact: emp.emergency_contact || '', emergency_phone: emp.emergency_phone || '',
    address: emp.address || '', blood_group: emp.blood_group || '',
  });
  errorMessage.value = '';
  showFormModal.value = true;
}

function confirmDelete(emp: Employee) { selectedEmployee.value = emp; showDeleteDialog.value = true; }
function closeFormModal() { showFormModal.value = false; selectedEmployee.value = null; errorMessage.value = ''; }

const filteredEmployees = computed(() => {
  if (!searchQuery.value.trim()) return employees.value;
  const q = searchQuery.value.toLowerCase();
  return employees.value.filter((e) =>
    e.first_name.toLowerCase().includes(q) || e.last_name.toLowerCase().includes(q) ||
    e.employee_code.toLowerCase().includes(q) || e.designation.toLowerCase().includes(q) ||
    e.email.toLowerCase().includes(q) || `${e.first_name} ${e.last_name}`.toLowerCase().includes(q),
  );
});

const pageNumbers = computed(() => {
  const total = meta.value.total_pages, current = currentPage.value;
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const pages: (number | string)[] = [1];
  if (current > 3) pages.push('...');
  for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) pages.push(i);
  if (current < total - 2) pages.push('...');
  if (total > 1) pages.push(total);
  return pages;
});

const inputCls = 'block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20';
const inputIconCls = inputCls.replace(' px-3', ' pl-10 pr-3');

watch([currentPage, deptFilter], () => fetchEmployees());
onMounted(() => fetchEmployees());
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-900">কর্মী / Employees</h2>
        <p class="mt-1 text-sm text-slate-500">Manage your organization's employee records.</p>
      </div>
      <button @click="openCreateModal" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 cursor-pointer">
        <UserPlus :size="18" /> নতুন কর্মী / Add Employee
      </button>
    </div>

    <!-- Error Banner -->
    <div v-if="errorMessage" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 flex items-center gap-2">
      <span class="text-sm text-red-700 flex-1">{{ errorMessage }}</span>
      <button @click="errorMessage = ''" class="text-red-500 hover:text-red-700 cursor-pointer"><X :size="16" /></button>
    </div>

    <!-- Search & Filter -->
    <div class="flex flex-col sm:flex-row gap-3">
      <div class="relative flex-1">
        <Search :size="18" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input v-model="searchQuery" type="text" placeholder="Search by name, code, designation…" class="block w-full rounded-lg border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20" />
      </div>
      <select v-model="deptFilter" class="rounded-lg border border-slate-200 bg-white py-2.5 px-3 text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 cursor-pointer">
        <option value="">All Departments</option>
        <option v-for="d in DEPARTMENTS" :key="d" :value="d">{{ d }}</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-6">
      <div class="animate-pulse space-y-4"><div v-for="i in 5" :key="i" class="h-12 bg-slate-100 rounded-lg"></div></div>
      <div class="mt-6 flex items-center justify-center gap-2 text-sm text-slate-400">
        <Loader2 :size="16" class="animate-spin" /> Loading employees…
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="employees.length === 0" class="flex flex-col items-center justify-center py-20 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <div class="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mb-4"><Users :size="32" class="text-slate-400" /></div>
      <h3 class="text-lg font-semibold text-slate-900">No employees found</h3>
      <p class="mt-1 text-sm text-slate-500 max-w-sm text-center">Get started by adding your first employee.</p>
      <button @click="openCreateModal" class="mt-4 inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 cursor-pointer">
        <UserPlus :size="16" /> নতুন কর্মী / Add Employee
      </button>
    </div>

    <!-- No Search Results -->
    <div v-else-if="filteredEmployees.length === 0 && searchQuery" class="flex flex-col items-center justify-center py-16 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <Search :size="32" class="text-slate-300 mb-3" />
      <p class="text-sm text-slate-500">No employees match "{{ searchQuery }}"</p>
    </div>

    <!-- Data Display -->
    <template v-else>
      <!-- Table (Desktop) -->
      <div class="hidden md:block rounded-xl bg-white border border-slate-200/80 shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200">
            <thead class="bg-slate-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Code</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Name</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Designation</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Department</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Phone</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Join Date</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="emp in filteredEmployees" :key="emp.id" class="hover:bg-slate-50/50 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center rounded-md bg-slate-100 px-2 py-1 text-xs font-mono font-medium text-slate-600">{{ emp.employee_code }}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center gap-3">
                    <div v-if="emp.avatar_url" class="w-9 h-9 rounded-full overflow-hidden flex-shrink-0">
                      <img :src="emp.avatar_url" :alt="emp.first_name" class="w-full h-full object-cover" />
                    </div>
                    <div v-else class="w-9 h-9 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                      <span class="text-xs font-bold text-emerald-700">{{ getInitials(emp) }}</span>
                    </div>
                    <div>
                      <span class="text-sm font-medium text-slate-900">{{ emp.first_name }} {{ emp.last_name }}</span>
                      <p v-if="emp.email" class="text-xs text-slate-400">{{ emp.email }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 text-sm text-slate-600">{{ emp.designation || '—' }}</td>
                <td class="px-6 py-4">
                  <span class="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">{{ emp.department || '—' }}</span>
                </td>
                <td class="px-6 py-4 text-sm text-slate-500">{{ emp.phone || '—' }}</td>
                <td class="px-6 py-4 text-sm text-slate-500">{{ emp.join_date ? formatDate(emp.join_date) : '—' }}</td>
                <td class="px-6 py-4">
                  <span :class="['inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium', emp.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600']">
                    <span :class="['w-1.5 h-1.5 rounded-full', emp.is_active ? 'bg-emerald-500' : 'bg-red-400']"></span>
                    {{ emp.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right">
                  <div class="flex items-center justify-end gap-1">
                    <button @click="openEditModal(emp)" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer" title="Edit"><Edit :size="16" /></button>
                    <button @click="confirmDelete(emp)" class="rounded-lg p-2 text-slate-400 hover:bg-red-50 hover:text-red-600 transition-colors cursor-pointer" title="Delete"><Trash2 :size="16" /></button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- Pagination -->
        <div v-if="meta.total_pages > 1" class="flex items-center justify-between border-t border-slate-200 px-6 py-3">
          <p class="text-sm text-slate-500">Showing {{ (currentPage - 1) * perPage + 1 }}–{{ Math.min(currentPage * perPage, meta.total) }} of {{ meta.total }}</p>
          <div class="flex items-center gap-1">
            <button @click="currentPage = Math.max(1, currentPage - 1)" :disabled="currentPage <= 1" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"><ChevronLeft :size="16" /></button>
            <template v-for="p in pageNumbers" :key="p">
              <span v-if="typeof p === 'string'" class="px-2 text-slate-400">…</span>
              <button v-else @click="currentPage = p" :class="['rounded-lg px-3 py-1.5 text-sm font-medium transition-colors cursor-pointer', p === currentPage ? 'bg-emerald-600 text-white' : 'text-slate-600 hover:bg-slate-100']">{{ p }}</button>
            </template>
            <button @click="currentPage = Math.min(meta.total_pages, currentPage + 1)" :disabled="currentPage >= meta.total_pages" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"><ChevronRight :size="16" /></button>
          </div>
        </div>
      </div>

      <!-- Cards (Mobile) -->
      <div class="md:hidden space-y-3">
        <div v-for="emp in filteredEmployees" :key="emp.id" class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-4 space-y-3">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div v-if="emp.avatar_url" class="w-10 h-10 rounded-full overflow-hidden flex-shrink-0">
                <img :src="emp.avatar_url" :alt="emp.first_name" class="w-full h-full object-cover" />
              </div>
              <div v-else class="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                <span class="text-sm font-bold text-emerald-700">{{ getInitials(emp) }}</span>
              </div>
              <div>
                <p class="text-sm font-semibold text-slate-900">{{ emp.first_name }} {{ emp.last_name }}</p>
                <p class="text-xs text-slate-400 font-mono">{{ emp.employee_code }}</p>
              </div>
            </div>
            <span :class="['inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium', emp.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600']">
              <span :class="['w-1.5 h-1.5 rounded-full', emp.is_active ? 'bg-emerald-500' : 'bg-red-400']"></span>
              {{ emp.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div class="grid grid-cols-2 gap-2 text-xs text-slate-500">
            <div v-if="emp.designation" class="flex items-center gap-1.5"><Briefcase :size="12" class="text-slate-400" />{{ emp.designation }}</div>
            <div v-if="emp.department" class="flex items-center gap-1.5"><Building2 :size="12" class="text-slate-400" />{{ emp.department }}</div>
            <div v-if="emp.phone" class="flex items-center gap-1.5"><Phone :size="12" class="text-slate-400" />{{ emp.phone }}</div>
            <div v-if="emp.join_date" class="flex items-center gap-1.5"><CalendarDays :size="12" class="text-slate-400" />{{ formatDate(emp.join_date) }}</div>
          </div>
          <div class="flex items-center gap-2 pt-1 border-t border-slate-100">
            <button @click="openEditModal(emp)" class="flex-1 flex items-center justify-center gap-1.5 rounded-lg border border-slate-200 py-2 text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer"><Edit :size="13" /> Edit</button>
            <button @click="confirmDelete(emp)" class="flex items-center justify-center rounded-lg border border-red-200 px-3 py-2 text-xs font-medium text-red-600 hover:bg-red-50 transition-colors cursor-pointer"><Trash2 :size="13" /></button>
          </div>
        </div>
        <!-- Mobile Pagination -->
        <div v-if="meta.total_pages > 1" class="flex items-center justify-center gap-2 pt-2">
          <button @click="currentPage = Math.max(1, currentPage - 1)" :disabled="currentPage <= 1" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 disabled:opacity-40 cursor-pointer"><ChevronLeft :size="16" /></button>
          <span class="text-sm text-slate-500">Page {{ currentPage }} of {{ meta.total_pages }}</span>
          <button @click="currentPage = Math.min(meta.total_pages, currentPage + 1)" :disabled="currentPage >= meta.total_pages" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 disabled:opacity-40 cursor-pointer"><ChevronRight :size="16" /></button>
        </div>
      </div>
    </template>

    <!-- Create / Edit Modal -->
    <Teleport to="body">
      <div v-if="showFormModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeFormModal"></div>
        <div class="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl bg-white shadow-2xl">
          <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 sticky top-0 bg-white rounded-t-2xl z-10">
            <h3 class="text-lg font-semibold text-slate-900">{{ isEditing ? 'Edit Employee' : 'নতুন কর্মী / Add Employee' }}</h3>
            <button @click="closeFormModal" class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer"><X :size="20" /></button>
          </div>
          <form @submit.prevent="saveEmployee" class="p-6 space-y-4">
            <div v-if="errorMessage" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700 flex items-center gap-2">
              <AlertCircle :size="16" class="flex-shrink-0" />{{ errorMessage }}
            </div>
            <!-- Name -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">First Name <span class="text-red-500">*</span></label>
                <input v-model="form.first_name" type="text" required placeholder="First name" :class="inputCls" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Last Name <span class="text-red-500">*</span></label>
                <input v-model="form.last_name" type="text" required placeholder="Last name" :class="inputCls" />
              </div>
            </div>
            <!-- Contact -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Email</label>
                <div class="relative"><Mail :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="form.email" type="email" placeholder="employee@example.com" :class="inputIconCls" /></div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Phone</label>
                <div class="relative"><Phone :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="form.phone" type="tel" placeholder="+880 1XXX-XXXXXX" :class="inputIconCls" /></div>
              </div>
            </div>
            <!-- Work -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Designation</label>
                <div class="relative"><Briefcase :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="form.designation" type="text" placeholder="e.g. Site Engineer" :class="inputIconCls" /></div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Department</label>
                <div class="relative"><Building2 :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <select v-model="form.department" :class="inputIconCls + ' cursor-pointer appearance-none'">
                    <option value="">— Select Department —</option>
                    <option v-for="d in DEPARTMENTS" :key="d" :value="d">{{ d }}</option>
                  </select>
                </div>
              </div>
            </div>
            <!-- Salary & Join Date -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Salary (BDT)</label>
                <input v-model="form.salary" type="number" min="0" step="1" placeholder="35000" :class="inputCls" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Join Date</label>
                <div class="relative"><CalendarDays :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="form.join_date" type="date" :class="inputIconCls" /></div>
              </div>
            </div>
            <!-- Blood Group -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Blood Group</label>
              <div class="relative"><Droplets :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <select v-model="form.blood_group" :class="inputIconCls + ' cursor-pointer appearance-none'">
                  <option value="">— Select —</option>
                  <option v-for="bg in BLOOD_GROUPS" :key="bg" :value="bg">{{ bg }}</option>
                </select>
              </div>
            </div>
            <!-- Address -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Address</label>
              <div class="relative"><MapPin :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="form.address" type="text" placeholder="Dhaka, Bangladesh" :class="inputIconCls" /></div>
            </div>
            <!-- Emergency Contact -->
            <div class="rounded-lg bg-amber-50/60 border border-amber-100 p-4 space-y-3">
              <p class="text-xs font-semibold text-amber-700 uppercase tracking-wide">Emergency Contact</p>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1">Contact Person</label>
                  <input v-model="form.emergency_contact" type="text" placeholder="Name" :class="inputCls" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1">Contact Phone</label>
                  <div class="relative"><Phone :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="form.emergency_phone" type="tel" placeholder="+880 1XXX-XXXXXX" :class="inputIconCls" /></div>
                </div>
              </div>
            </div>
            <!-- Actions -->
            <div class="flex items-center justify-end gap-3 pt-2">
              <button type="button" @click="closeFormModal" class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
              <button type="submit" :disabled="saving" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer">
                <Loader2 v-if="saving" :size="16" class="animate-spin" />{{ isEditing ? 'Update Employee' : 'Add Employee' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation Dialog -->
    <Teleport to="body">
      <div v-if="showDeleteDialog" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showDeleteDialog = false"></div>
        <div class="relative w-full max-w-sm rounded-2xl bg-white shadow-2xl p-6 text-center">
          <div class="mx-auto mb-4 w-14 h-14 rounded-full bg-red-50 flex items-center justify-center"><Trash2 :size="24" class="text-red-500" /></div>
          <h3 class="text-lg font-semibold text-slate-900">Delete Employee?</h3>
          <p class="mt-2 text-sm text-slate-500">Are you sure you want to delete <strong class="text-slate-700">{{ selectedEmployee?.first_name }} {{ selectedEmployee?.last_name }}</strong> ({{ selectedEmployee?.employee_code }})? This action cannot be undone.</p>
          <div class="mt-6 flex items-center gap-3">
            <button @click="showDeleteDialog = false" class="flex-1 rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
            <button @click="deleteEmployee" :disabled="deleting" class="flex-1 inline-flex items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60 transition-colors cursor-pointer">
              <Loader2 v-if="deleting" :size="16" class="animate-spin" />Delete
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
