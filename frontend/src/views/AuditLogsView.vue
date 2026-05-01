<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { Search, Shield, Loader2, ChevronLeft, ChevronRight } from '@lucide/vue';
import api from '@/lib/api';

const { locale } = useI18n();
const isBangla = computed(() => locale.value === 'bn');
import { computed } from 'vue';

interface AuditLog {
  id: string;
  user_email: string;
  action: string;
  entity_type: string;
  entity_id: string;
  ip_address: string;
  old_values: any;
  new_values: any;
  created_at: string;
}

const logs = ref<AuditLog[]>([]);
const loading = ref(true);
const searchQuery = ref('');
const currentPage = ref(1);
const totalPages = ref(1);
const total = ref(0);
const perPage = 20;

const actionColors: Record<string, string> = {
  create: 'bg-emerald-100 text-emerald-700',
  update: 'bg-blue-100 text-blue-700',
  delete: 'bg-red-100 text-red-700',
  login: 'bg-slate-100 text-slate-700',
  invite: 'bg-purple-100 text-purple-700',
  deactivate: 'bg-amber-100 text-amber-700',
  activate: 'bg-emerald-100 text-emerald-700',
};

const filteredLogs = computed(() => {
  if (!searchQuery.value) return logs.value;
  const q = searchQuery.value.toLowerCase();
  return logs.value.filter(
    (l) =>
      l.user_email?.toLowerCase().includes(q) ||
      l.action?.toLowerCase().includes(q) ||
      l.entity_type?.toLowerCase().includes(q)
  );
});

async function fetchLogs() {
  loading.value = true;
  try {
    const { data } = await api.get('/audit-logs', { params: { page: currentPage.value, per_page: perPage } });
    logs.value = data.data || [];
    total.value = data.meta?.total || 0;
    totalPages.value = data.meta?.total_pages || 1;
  } catch { logs.value = []; } finally { loading.value = false; }
}

function formatDate(dt: string) {
  return new Date(dt).toLocaleString(isBangla.value ? 'bn-BD' : 'en-US', { dateStyle: 'medium', timeStyle: 'short' });
}

function getActionColor(action: string) {
  const base = action.split('.')[0];
  return actionColors[base] || 'bg-slate-100 text-slate-600';
}

const pageNumbers = computed(() => {
  const pages: (number | string)[] = [];
  if (totalPages.value <= 7) { for (let i = 1; i <= totalPages.value; i++) pages.push(i); }
  else {
    pages.push(1);
    if (currentPage.value > 3) pages.push('...');
    for (let i = Math.max(2, currentPage.value - 1); i <= Math.min(totalPages.value - 1, currentPage.value + 1); i++) pages.push(i);
    if (currentPage.value < totalPages.value - 2) pages.push('...');
    pages.push(totalPages.value);
  }
  return pages;
});

const startItem = computed(() => (currentPage.value - 1) * perPage + 1);
const endItem = computed(() => Math.min(currentPage.value * perPage, total.value));

onMounted(fetchLogs);
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-900">{{ isBangla ? 'অডিট লগ' : 'Audit Logs' }}</h2>
        <p class="mt-1 text-sm text-slate-500">{{ isBangla ? 'সমস্ত কার্যক্রমের লগ দেখুন' : 'View all activity logs' }}</p>
      </div>
    </div>

    <!-- Search -->
    <div class="flex gap-3">
      <div class="relative flex-1 max-w-sm">
        <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input v-model="searchQuery" type="text" :placeholder="isBangla ? 'অ্যাকশন, ইমেইল খুঁজুন...' : 'Search action, email...'"
          class="w-full rounded-lg border border-slate-300 bg-white py-2 pl-9 pr-3 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20" />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 :size="32" class="animate-spin text-emerald-600" />
      <span class="ml-3 text-sm text-slate-500">{{ isBangla ? 'লোড হচ্ছে...' : 'Loading...' }}</span>
    </div>

    <!-- Empty -->
    <div v-else-if="logs.length === 0" class="flex flex-col items-center justify-center py-20 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <Shield :size="48" class="text-slate-300 mb-4" />
      <h3 class="text-lg font-semibold text-slate-900">{{ isBangla ? 'কোন লগ নেই' : 'No Logs Found' }}</h3>
    </div>

    <!-- Desktop Table -->
    <div v-else class="rounded-xl bg-white border border-slate-200/80 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 border-b border-slate-200">
            <tr>
              <th class="px-4 py-3 text-left font-medium text-slate-500">{{ isBangla ? 'সময়' : 'Timestamp' }}</th>
              <th class="px-4 py-3 text-left font-medium text-slate-500">{{ isBangla ? 'ব্যবহারকারী' : 'User' }}</th>
              <th class="px-4 py-3 text-left font-medium text-slate-500">{{ isBangla ? 'অ্যাকশন' : 'Action' }}</th>
              <th class="px-4 py-3 text-left font-medium text-slate-500">Entity</th>
              <th class="px-4 py-3 text-left font-medium text-slate-500">IP</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="log in filteredLogs" :key="log.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="px-4 py-3 text-slate-600 whitespace-nowrap">{{ formatDate(log.created_at) }}</td>
              <td class="px-4 py-3 text-slate-900 font-medium">{{ log.user_email }}</td>
              <td class="px-4 py-3">
                <span :class="['inline-flex px-2 py-0.5 rounded-full text-xs font-medium', getActionColor(log.action)]">
                  {{ log.action }}
                </span>
              </td>
              <td class="px-4 py-3 text-slate-600">{{ log.entity_type }}<span class="text-slate-400 text-xs ml-1">#{{ log.entity_id?.slice(0, 8) }}</span></td>
              <td class="px-4 py-3 text-slate-500 font-mono text-xs">{{ log.ip_address }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && totalPages > 1" class="flex items-center justify-between">
      <p class="text-sm text-slate-500">
        {{ startItem }}–{{ endItem }} {{ isBangla ? 'এর মধ্যে' : 'of' }} {{ total }}
      </p>
      <div class="flex items-center gap-1">
        <button @click="currentPage = Math.max(1, currentPage - 1); fetchLogs()" :disabled="currentPage === 1"
          class="p-2 rounded-lg hover:bg-slate-100 disabled:opacity-40 cursor-pointer"><ChevronLeft :size="16" /></button>
        <button v-for="p in pageNumbers" :key="p" @click="typeof p === 'number' && (currentPage = p, fetchLogs())"
          :class="['px-3 py-1.5 rounded-lg text-sm font-medium cursor-pointer', currentPage === p ? 'bg-emerald-600 text-white' : 'hover:bg-slate-100 text-slate-600']">
          {{ p }}
        </button>
        <button @click="currentPage = Math.min(totalPages, currentPage + 1); fetchLogs()" :disabled="currentPage === totalPages"
          class="p-2 rounded-lg hover:bg-slate-100 disabled:opacity-40 cursor-pointer"><ChevronRight :size="16" /></button>
      </div>
    </div>
  </div>
</template>
