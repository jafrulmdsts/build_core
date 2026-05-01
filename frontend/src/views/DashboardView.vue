<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/features/auth/store';
import api from '@/lib/api';
import {
  FolderKanban,
  UserCheck,
  Wrench,
  Receipt,
  TrendingUp,
  TrendingDown,
  Plus,
  ArrowRight,
  Clock,
  CheckCircle2,
  AlertCircle,
  UserPlus,
  FileText,
  Building2,
  Shield,
} from '@lucide/vue';

const { locale } = useI18n();
const isBangla = computed(() => locale.value === 'bn');
const authStore = useAuthStore();

const loading = ref(true);

// Real stats from API
const statsData = ref({ projects: 0, employees: 0, contractors: 0, expenses: 0 });
const recentActivities = ref<any[]>([]);

const stats = computed(() => [
  {
    label: isBangla.value ? 'মোট প্রকল্প' : 'Total Projects',
    value: String(statsData.value.projects),
    trend: isBangla.value ? 'সক্রিয় প্রকল্প' : 'Active projects',
    trendUp: true,
    icon: FolderKanban,
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-600',
  },
  {
    label: isBangla.value ? 'সক্রিয় কর্মী' : 'Active Employees',
    value: String(statsData.value.employees),
    trend: isBangla.value ? 'মোট কর্মী' : 'Total employees',
    trendUp: true,
    icon: UserCheck,
    bgColor: 'bg-emerald-50',
    textColor: 'text-emerald-600',
  },
  {
    label: isBangla.value ? 'চুক্তিকার' : 'Contractors',
    value: String(statsData.value.contractors),
    trend: isBangla.value ? 'নিবন্ধিত চুক্তিকার' : 'Registered contractors',
    trendUp: true,
    icon: Wrench,
    bgColor: 'bg-amber-50',
    textColor: 'text-amber-600',
  },
  {
    label: isBangla.value ? 'মাসিক ব্যয়' : 'Monthly Expenses',
    value: `৳${statsData.value.expenses.toLocaleString()}`,
    trend: isBangla.value ? 'এই মাসে' : 'This month',
    trendUp: false,
    icon: Receipt,
    bgColor: 'bg-purple-50',
    textColor: 'text-purple-600',
  },
]);

const quickActions = computed(() => {
  const actions = [
    { label: isBangla.value ? 'নতুন প্রকল্প' : 'New Project', icon: Plus, path: '/projects' },
    { label: isBangla.value ? 'কর্মী যোগ করুন' : 'Add Employee', icon: UserPlus, path: '/employees' },
    { label: isBangla.value ? 'ব্যয় দেখুন' : 'View Expenses', icon: TrendingUp, path: '/expenses' },
    { label: isBangla.value ? 'ভূমিকা পরিচালনা' : 'Manage Roles', icon: Shield, path: '/roles' },
  ];
  return actions;
});

async function fetchDashboardData() {
  loading.value = true;
  try {
    const [projectsRes, employeesRes, contractorsRes, expensesRes, auditRes] = await Promise.allSettled([
      api.get('/projects', { params: { page: 1, per_page: 1 } }),
      api.get('/employees', { params: { page: 1, per_page: 1 } }),
      api.get('/contractors', { params: { page: 1, per_page: 1 } }),
      api.get('/expenses', { params: { page: 1, per_page: 1 } }),
      api.get('/audit-logs', { params: { page: 1, per_page: 5 } }),
    ]);

    statsData.value.projects = projectsRes.status === 'fulfilled' ? (projectsRes.value.data.meta?.total || 0) : 0;
    statsData.value.employees = employeesRes.status === 'fulfilled' ? (employeesRes.value.data.meta?.total || 0) : 0;
    statsData.value.contractors = contractorsRes.status === 'fulfilled' ? (contractorsRes.value.data.meta?.total || 0) : 0;
    statsData.value.expenses = expensesRes.status === 'fulfilled' ? (expensesRes.value.data.meta?.total || 0) : 0;

    if (auditRes.status === 'fulfilled') {
      const logs = auditRes.value.data.data || [];
      recentActivities.value = logs.map((log: any) => {
        const actionBase = log.action?.split('.')[0] || 'update';
        const icons: Record<string, any> = { create: CheckCircle2, update: Shield, delete: AlertCircle, login: UserPlus, invite: UserPlus };
        const types: Record<string, string> = { create: 'success', update: 'success', delete: 'warning', login: 'success', invite: 'success', deactivate: 'warning', activate: 'success' };
        return {
          id: log.id,
          text: `${log.user_email} — ${log.action} on ${log.entity_type}`,
          time: new Date(log.created_at).toLocaleString(isBangla.value ? 'bn-BD' : 'en-US', { dateStyle: 'short', timeStyle: 'short' }),
          type: types[actionBase] || 'success',
          icon: icons[actionBase] || FileText,
        };
      });
    }
  } catch {} finally { loading.value = false; }
}

onMounted(fetchDashboardData);
</script>

<template>
  <div class="space-y-6">
    <!-- Welcome Header -->
    <div>
      <h2 class="text-2xl font-bold text-slate-900">{{ isBangla ? 'স্বাগতম!' : 'Welcome back!' }} {{ authStore.getFullName() }}</h2>
      <p class="mt-1 text-sm text-slate-500">{{ isBangla.value ? 'আজকে আপনার সংস্থার কার্যক্রম' : "Here's what's happening with your organization today." }}</p>
    </div>

    <!-- Stats Cards Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 sm:gap-6">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-5 sm:p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="space-y-3">
            <p class="text-sm font-medium text-slate-500">{{ stat.label }}</p>
            <p class="text-2xl sm:text-3xl font-bold text-slate-900">{{ stat.value }}</p>
          </div>
          <div :class="['w-10 h-10 rounded-lg flex items-center justify-center', stat.bgColor]">
            <component :is="stat.icon" :size="20" :class="stat.textColor" />
          </div>
        </div>
        <div class="mt-3 flex items-center gap-1.5">
          <TrendingUp
            v-if="stat.trendUp"
            :size="14"
            class="text-emerald-500"
          />
          <TrendingDown
            v-else
            :size="14"
            class="text-red-500"
          />
          <span :class="['text-xs font-medium', stat.trendUp ? 'text-emerald-600' : 'text-red-600']">
            {{ stat.trend }}
          </span>
        </div>
      </div>
    </div>

    <!-- Content Grid: Recent Activity + Quick Actions -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
      <!-- Recent Activity -->
      <div class="lg:col-span-2 rounded-xl bg-white border border-slate-200/80 shadow-sm">
        <div class="flex items-center justify-between px-5 sm:px-6 py-4 border-b border-slate-100">
          <h3 class="text-base font-semibold text-slate-900">{{ isBangla ? 'সাম্প্রতিক কার্যক্রম' : 'Recent Activity' }}</h3>
          <router-link to="/audit-logs" class="text-sm font-medium text-emerald-600 hover:text-emerald-700 transition-colors">
            {{ isBangla ? 'সব দেখুন' : 'View all' }}
          </router-link>
        </div>
        <div class="divide-y divide-slate-100">
          <div
            v-for="activity in recentActivities"
            :key="activity.id"
            class="flex items-start gap-3 px-5 sm:px-6 py-3.5 hover:bg-slate-50/50 transition-colors"
          >
            <div
              :class="[
                'mt-0.5 w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
                activity.type === 'success' ? 'bg-emerald-50' : activity.type === 'warning' ? 'bg-amber-50' : 'bg-slate-100',
              ]"
            >
              <component
                :is="activity.icon"
                :size="16"
                :class="[
                  activity.type === 'success' ? 'text-emerald-500' : activity.type === 'warning' ? 'text-amber-500' : 'text-slate-500',
                ]"
              />
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm text-slate-700">{{ activity.text }}</p>
              <p class="mt-0.5 text-xs text-slate-400">{{ activity.time }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="rounded-xl bg-white border border-slate-200/80 shadow-sm">
        <div class="px-5 sm:px-6 py-4 border-b border-slate-100">
          <h3 class="text-base font-semibold text-slate-900">{{ isBangla ? 'দ্রুত কার্য' : 'Quick Actions' }}</h3>
        </div>
        <div class="p-4 sm:p-5 space-y-2">
          <router-link
            v-for="action in quickActions"
            :key="action.label"
            :to="action.path"
            class="flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium text-slate-700 hover:bg-emerald-50 hover:text-emerald-700 transition-all group"
          >
            <div class="w-8 h-8 rounded-lg bg-slate-100 group-hover:bg-emerald-100 flex items-center justify-center transition-colors">
              <component :is="action.icon" :size="16" class="text-slate-500 group-hover:text-emerald-600 transition-colors" />
            </div>
            <span>{{ action.label }}</span>
            <ArrowRight :size="14" class="ml-auto text-slate-300 group-hover:text-emerald-500 transition-colors" />
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>
