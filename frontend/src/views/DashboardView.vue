<script setup lang="ts">
import { ref } from 'vue';
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
} from '@lucide/vue';

const stats = ref([
  {
    label: 'Total Projects',
    value: '12',
    trend: '+3 this month',
    trendUp: true,
    icon: FolderKanban,
    color: 'bg-blue-500',
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-600',
  },
  {
    label: 'Active Employees',
    value: '48',
    trend: '+5 this month',
    trendUp: true,
    icon: UserCheck,
    color: 'bg-emerald-500',
    bgColor: 'bg-emerald-50',
    textColor: 'text-emerald-600',
  },
  {
    label: 'Contractors',
    value: '15',
    trend: '+2 this month',
    trendUp: true,
    icon: Wrench,
    color: 'bg-amber-500',
    bgColor: 'bg-amber-50',
    textColor: 'text-amber-600',
  },
  {
    label: 'Monthly Expenses',
    value: '৳2.4L',
    trend: '-12% vs last',
    trendUp: false,
    icon: Receipt,
    color: 'bg-purple-500',
    bgColor: 'bg-purple-50',
    textColor: 'text-purple-600',
  },
]);

const recentActivities = ref([
  {
    id: 1,
    text: 'New project "Dhaka Tower Phase 2" was created',
    time: '2 hours ago',
    type: 'success' as const,
    icon: CheckCircle2,
  },
  {
    id: 2,
    text: 'Employee Karim Hossain joined the organization',
    time: '5 hours ago',
    type: 'success' as const,
    icon: UserPlus,
  },
  {
    id: 3,
    text: 'Expense report for March submitted for approval',
    time: '1 day ago',
    type: 'pending' as const,
    icon: Clock,
  },
  {
    id: 4,
    text: 'Contractor payment deadline approaching',
    time: '1 day ago',
    type: 'warning' as const,
    icon: AlertCircle,
  },
  {
    id: 5,
    text: 'Role "Site Manager" permissions updated',
    time: '2 days ago',
    type: 'success' as const,
    icon: CheckCircle2,
  },
]);

const quickActions = ref([
  { label: 'New Project', icon: Plus, path: '/projects' },
  { label: 'Add Employee', icon: UserPlus, path: '/employees' },
  { label: 'View Reports', icon: TrendingUp, path: '/expenses' },
  { label: 'Manage Roles', icon: ArrowRight, path: '/roles' },
]);
</script>

<template>
  <div class="space-y-6">
    <!-- Welcome Header -->
    <div>
      <h2 class="text-2xl font-bold text-slate-900">Welcome back!</h2>
      <p class="mt-1 text-sm text-slate-500">Here's what's happening with your organization today.</p>
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
          <h3 class="text-base font-semibold text-slate-900">Recent Activity</h3>
          <button class="text-sm font-medium text-emerald-600 hover:text-emerald-700 transition-colors cursor-pointer">
            View all
          </button>
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
          <h3 class="text-base font-semibold text-slate-900">Quick Actions</h3>
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
