<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import {
  FolderKanban, Plus, Search, Pencil, Trash2, MapPin, Calendar,
  ChevronLeft, ChevronRight, Loader2, X, AlertTriangle, DollarSign,
  CheckCircle2, PauseCircle, XCircle, LayoutGrid, Building2,
} from '@lucide/vue';
import api from '@/lib/api';
import { useAuthStore } from '@/features/auth/store';

interface Project {
  id: string; name: string; description: string; location: string;
  start_date: string; end_date: string; budget: number; budget_used: number;
  status: string; client_name: string; client_phone: string;
  organization_id: string; created_at: string;
}

interface Meta { page: number; per_page: number; total: number; total_pages: number; }

const ST: Record<string, { c: string; bg: string; ic: any; l: string }> = {
  active:    { c: 'text-emerald-700', bg: 'bg-emerald-50 ring-emerald-600/20',  ic: CheckCircle2, l: 'Active' },
  completed: { c: 'text-blue-700',    bg: 'bg-blue-50 ring-blue-600/20',        ic: CheckCircle2, l: 'Completed' },
  paused:    { c: 'text-amber-700',   bg: 'bg-amber-50 ring-amber-600/20',      ic: PauseCircle,  l: 'Paused' },
  cancelled: { c: 'text-red-700',     bg: 'bg-red-50 ring-red-600/20',          ic: XCircle,      l: 'Cancelled' },
  planned:   { c: 'text-slate-600',   bg: 'bg-slate-50 ring-slate-500/20',      ic: LayoutGrid,   l: 'Planned' },
};
const ST_OPT = [
  { v: '', l: 'All Statuses' }, { v: 'active', l: 'Active' }, { v: 'completed', l: 'Completed' },
  { v: 'paused', l: 'Paused' }, { v: 'cancelled', l: 'Cancelled' }, { v: 'planned', l: 'Planned' },
];

const auth = useAuthStore();
const projects = ref<Project[]>([]);
const meta = ref<Meta>({ page: 1, per_page: 20, total: 0, total_pages: 0 });
const loading = ref(false);
const q = ref('');
const sFilter = ref('');
const page = ref(1);
const showModal = ref(false);
const editing = ref(false);
const submitting = ref(false);
const formErr = ref('');
const showDel = ref(false);
const delTarget = ref<Project | null>(null);
const deleting = ref(false);

const blank = () => ({
  id: '', name: '', description: '', location: '', start_date: '', end_date: '',
  budget: '', status: 'planned', client_name: '', client_phone: '',
});
const form = reactive<Record<string, string>>(blank());

const fmtCurrency = (v: number) =>
  v >= 1e7 ? `${(v / 1e7).toFixed(1)}Cr` : v >= 1e5 ? `${(v / 1e5).toFixed(1)}L` : v >= 1e3 ? `${(v / 1e3).toFixed(1)}K` : v.toLocaleString('en-BD');
const fmtDate = (d: string) => d ? new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : '—';
const pct = (p: Project) => (!p.budget ? 0 : Math.min(100, Math.round(((p.budget_used || 0) / p.budget) * 100)));
const pColor = (v: number) => v >= 90 ? 'bg-red-500' : v >= 70 ? 'bg-amber-500' : 'bg-emerald-500';

const stats = computed(() => {
  const tb = projects.value.reduce((s, p) => s + (p.budget || 0), 0);
  return [
    { label: 'Total Projects', value: meta.value.total, icon: FolderKanban, bg: 'bg-emerald-50', tx: 'text-emerald-600' },
    { label: 'Active', value: projects.value.filter(p => p.status === 'active').length, icon: CheckCircle2, bg: 'bg-blue-50', tx: 'text-blue-600' },
    { label: 'Completed', value: projects.value.filter(p => p.status === 'completed').length, icon: Building2, bg: 'bg-amber-50', tx: 'text-amber-600' },
    { label: 'Total Budget', value: `৳${fmtCurrency(tb)}`, icon: DollarSign, bg: 'bg-purple-50', tx: 'text-purple-600' },
  ];
});

const pages = computed(() => {
  const t = meta.value.total_pages, c = meta.value.page, r: (number|string)[] = [];
  if (t <= 5) { for (let i = 1; i <= t; i++) r.push(i); }
  else { r.push(1); if (c > 3) r.push('…'); for (let i = Math.max(2, c - 1); i <= Math.min(t - 1, c + 1); i++) r.push(i); if (c < t - 2) r.push('…'); r.push(t); }
  return r;
});

async function fetch() {
  loading.value = true;
  try {
    const p: any = { page: page.value, per_page: 20 };
    if (q.value.trim()) p.search = q.value.trim();
    if (sFilter.value) p.status = sFilter.value;
    const { data } = await api.get('/projects', { params: p });
    projects.value = data.data || []; meta.value = data.meta || { page: 1, per_page: 20, total: 0, total_pages: 0 };
  } catch { projects.value = []; } finally { loading.value = false; }
}

async function submit() {
  formErr.value = '';
  if (!form.name.trim()) { formErr.value = 'Project name is required.'; return; }
  submitting.value = true;
  try {
    const payload: any = { ...form, budget: form.budget ? Number(form.budget) : 0 };
    if (editing.value) await api.put(`/projects/${form.id}`, payload);
    else { payload.organization_id = auth.user?.organization_id; await api.post('/projects', payload); }
    showModal.value = false; await fetch();
  } catch (e: any) { formErr.value = e.response?.data?.error?.message || 'Failed to save project.'; }
  finally { submitting.value = false; }
}

async function doDelete() {
  if (!delTarget.value) return; deleting.value = true;
  try { await api.delete(`/projects/${delTarget.value.id}`); showDel.value = false; delTarget.value = null; await fetch(); } catch {} finally { deleting.value = false; }
}

function openCreate() { Object.assign(form, blank()); editing.value = false; formErr.value = ''; showModal.value = true; }
function openEdit(p: Project) {
  Object.assign(form, { id: p.id, name: p.name, description: p.description||'', location: p.location||'',
    start_date: p.start_date||'', end_date: p.end_date||'', budget: p.budget ? String(p.budget) : '',
    status: p.status, client_name: p.client_name||'', client_phone: p.client_phone||'' });
  editing.value = true; formErr.value = ''; showModal.value = true;
}

watch([q, sFilter], () => { page.value = 1; fetch(); });
watch(page, fetch);
onMounted(fetch);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <div>
        <h2 class="text-2xl font-bold text-slate-900">প্রকল্প / Projects</h2>
        <p class="mt-1 text-sm text-slate-500">Track and manage all construction projects.</p>
      </div>
      <button @click="openCreate" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 transition-colors cursor-pointer">
        <Plus :size="18" /> নতুন প্রকল্প / New Project
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      <div v-for="s in stats" :key="s.label" class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-4 sm:p-5 hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <p class="text-xs sm:text-sm font-medium text-slate-500 truncate">{{ s.label }}</p>
          <div :class="['w-8 h-8 sm:w-9 sm:h-9 rounded-lg flex items-center justify-center flex-shrink-0', s.bg]">
            <component :is="s.icon" :size="16" :class="s.tx" />
          </div>
        </div>
        <p class="mt-2 text-xl sm:text-2xl font-bold text-slate-900 truncate">{{ s.value }}</p>
      </div>
    </div>

    <!-- Search & Filter -->
    <div class="flex flex-col sm:flex-row gap-3">
      <div class="relative flex-1">
        <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        <input v-model="q" type="text" placeholder="Search projects by name, location, client…" class="w-full rounded-lg border border-slate-200 bg-white py-2.5 pl-9 pr-3 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
      </div>
      <select v-model="sFilter" class="rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-700 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition cursor-pointer">
        <option v-for="o in ST_OPT" :key="o.v" :value="o.v">{{ o.l }}</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 :size="32" class="animate-spin text-emerald-500" />
      <span class="ml-3 text-sm text-slate-500">Loading projects…</span>
    </div>

    <!-- Empty -->
    <div v-else-if="!projects.length" class="flex flex-col items-center justify-center py-20 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <div class="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mb-4"><FolderKanban :size="32" class="text-slate-400" /></div>
      <h3 class="text-lg font-semibold text-slate-900">No Projects Found</h3>
      <p class="mt-1 text-sm text-slate-500 max-w-sm text-center">{{ q || sFilter ? 'Try adjusting your search or filter.' : 'Get started by creating your first project.' }}</p>
      <button v-if="!q && !sFilter" @click="openCreate" class="mt-4 inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 transition-colors cursor-pointer"><Plus :size="16" /> Create Project</button>
    </div>

    <!-- Desktop Table -->
    <div v-if="!loading && projects.length" class="hidden lg:block rounded-xl bg-white border border-slate-200/80 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
          <thead class="bg-slate-50/80 border-b border-slate-200">
            <tr>
              <th class="px-5 py-3 font-semibold text-slate-600">Name</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Location</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Status</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Budget</th>
              <th class="px-5 py-3 font-semibold text-slate-600 min-w-[140px]">Progress</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Dates</th>
              <th class="px-5 py-3 font-semibold text-slate-600 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="p in projects" :key="p.id" class="hover:bg-slate-50/60 transition-colors">
              <td class="px-5 py-3.5">
                <div class="font-medium text-slate-900 truncate max-w-[200px]">{{ p.name }}</div>
                <div v-if="p.client_name" class="text-xs text-slate-400 truncate max-w-[200px]">{{ p.client_name }}</div>
              </td>
              <td class="px-5 py-3.5"><span class="inline-flex items-center gap-1 text-slate-600"><MapPin :size="12" class="text-slate-400 flex-shrink-0" /><span class="truncate max-w-[150px]">{{ p.location || '—' }}</span></span></td>
              <td class="px-5 py-3.5">
                <span :class="['inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset', ST[p.status]?.bg, ST[p.status]?.c]">
                  <component :is="ST[p.status]?.ic" :size="12" />{{ ST[p.status]?.l || p.status }}
                </span>
              </td>
              <td class="px-5 py-3.5 font-medium text-slate-700 whitespace-nowrap">৳{{ fmtCurrency(p.budget) }}</td>
              <td class="px-5 py-3.5">
                <div class="flex items-center gap-2">
                  <div class="flex-1 h-2 rounded-full bg-slate-100 overflow-hidden"><div :class="['h-full rounded-full transition-all', pColor(pct(p))]" :style="{ width: pct(p) + '%' }"></div></div>
                  <span class="text-xs font-medium text-slate-500 w-8 text-right">{{ pct(p) }}%</span>
                </div>
              </td>
              <td class="px-5 py-3.5 whitespace-nowrap"><span class="inline-flex items-center gap-1 text-xs text-slate-500"><Calendar :size="12" />{{ fmtDate(p.start_date) }} – {{ fmtDate(p.end_date) }}</span></td>
              <td class="px-5 py-3.5 text-right">
                <button @click="openEdit(p)" class="p-1.5 rounded-lg text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 transition-colors cursor-pointer"><Pencil :size="16" /></button>
                <button @click="delTarget = p; showDel = true" class="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors cursor-pointer"><Trash2 :size="16" /></button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Mobile Cards -->
    <div v-if="!loading && projects.length" class="lg:hidden space-y-3">
      <div v-for="p in projects" :key="p.id" class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-4 space-y-3">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0"><h4 class="font-semibold text-slate-900 truncate">{{ p.name }}</h4><p v-if="p.client_name" class="text-xs text-slate-400 truncate">{{ p.client_name }}</p></div>
          <span :class="['inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset flex-shrink-0', ST[p.status]?.bg, ST[p.status]?.c]">{{ ST[p.status]?.l || p.status }}</span>
        </div>
        <div class="flex items-center gap-1 text-xs text-slate-500"><MapPin :size="12" class="text-slate-400" /><span class="truncate">{{ p.location || '—' }}</span></div>
        <div class="flex items-center justify-between text-xs text-slate-500">
          <span class="inline-flex items-center gap-1"><Calendar :size="12" />{{ fmtDate(p.start_date) }} – {{ fmtDate(p.end_date) }}</span>
          <span class="font-medium text-slate-700">৳{{ fmtCurrency(p.budget) }}</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="flex-1 h-2 rounded-full bg-slate-100 overflow-hidden"><div :class="['h-full rounded-full transition-all', pColor(pct(p))]" :style="{ width: pct(p) + '%' }"></div></div>
          <span class="text-xs font-medium text-slate-500 w-8 text-right">{{ pct(p) }}%</span>
        </div>
        <div class="flex items-center gap-2 pt-1 border-t border-slate-100">
          <button @click="openEdit(p)" class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 transition-colors cursor-pointer"><Pencil :size="13" /> Edit</button>
          <button @click="delTarget = p; showDel = true" class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-red-700 bg-red-50 hover:bg-red-100 transition-colors cursor-pointer"><Trash2 :size="13" /> Delete</button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="meta.total_pages > 1" class="flex items-center justify-between">
      <p class="text-sm text-slate-500">Showing {{ (meta.page - 1) * meta.per_page + 1 }}–{{ Math.min(meta.page * meta.per_page, meta.total) }} of {{ meta.total }}</p>
      <nav class="flex items-center gap-1">
        <button @click="page = meta.page - 1" :disabled="meta.page <= 1" class="p-2 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors cursor-pointer"><ChevronLeft :size="18" /></button>
        <button v-for="pg in pages" :key="pg" @click="typeof pg === 'number' && (page = pg)" :disabled="typeof pg !== 'number'"
          :class="['w-9 h-9 rounded-lg text-sm font-medium transition-colors cursor-pointer', pg === meta.page ? 'bg-emerald-600 text-white' : typeof pg === 'number' ? 'text-slate-600 hover:bg-slate-100' : 'text-slate-400 cursor-default']">{{ pg }}</button>
        <button @click="page = meta.page + 1" :disabled="meta.page >= meta.total_pages" class="p-2 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors cursor-pointer"><ChevronRight :size="18" /></button>
      </nav>
    </div>

    <!-- Create / Edit Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showModal = false"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 sticky top-0 bg-white rounded-t-2xl z-10">
              <h3 class="text-lg font-semibold text-slate-900">{{ editing ? 'Edit Project' : 'নতুন প্রকল্প / New Project' }}</h3>
              <button @click="showModal = false" class="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"><X :size="20" /></button>
            </div>
            <form @submit.prevent="submit" class="p-6 space-y-4">
              <div v-if="formErr" class="flex items-center gap-2 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700"><AlertTriangle :size="16" class="flex-shrink-0" />{{ formErr }}</div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Project Name <span class="text-red-500">*</span></label>
                <input v-model="form.name" type="text" required placeholder="e.g. Dhaka Tower Phase 2" class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Description</label>
                <textarea v-model="form.description" rows="2" placeholder="Brief project description…" class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition resize-none"></textarea>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div><label class="block text-sm font-medium text-slate-700 mb-1">Location</label><input v-model="form.location" type="text" placeholder="e.g. Gulshan, Dhaka" class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" /></div>
                <div><label class="block text-sm font-medium text-slate-700 mb-1">Status</label><select v-model="form.status" class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition cursor-pointer"><option v-for="o in ST_OPT.filter(x => x.v)" :key="o.v" :value="o.v">{{ o.l }}</option></select></div>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div><label class="block text-sm font-medium text-slate-700 mb-1">Start Date</label><input v-model="form.start_date" type="date" class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" /></div>
                <div><label class="block text-sm font-medium text-slate-700 mb-1">End Date</label><input v-model="form.end_date" type="date" class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" /></div>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div><label class="block text-sm font-medium text-slate-700 mb-1">Budget (৳)</label><input v-model="form.budget" type="number" min="0" step="1" placeholder="e.g. 5000000" class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" /></div>
                <div><label class="block text-sm font-medium text-slate-700 mb-1">Client Phone</label><input v-model="form.client_phone" type="tel" placeholder="+880…" class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" /></div>
              </div>
              <div><label class="block text-sm font-medium text-slate-700 mb-1">Client Name</label><input v-model="form.client_name" type="text" placeholder="e.g. ABC Corp" class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" /></div>
              <div class="flex items-center justify-end gap-3 pt-2">
                <button type="button" @click="showModal = false" class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
                <button type="submit" :disabled="submitting" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-emerald-700 disabled:opacity-60 transition-colors cursor-pointer">
                  <Loader2 v-if="submitting" :size="16" class="animate-spin" />{{ editing ? 'Update Project' : 'Create Project' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Delete Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showDel" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showDel = false"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 text-center">
            <div class="mx-auto w-12 h-12 rounded-full bg-red-50 flex items-center justify-center mb-4"><AlertTriangle :size="24" class="text-red-600" /></div>
            <h3 class="text-lg font-semibold text-slate-900">Delete Project?</h3>
            <p class="mt-2 text-sm text-slate-500">Are you sure you want to delete <span class="font-medium text-slate-700">"{{ delTarget?.name }}"</span>? This action cannot be undone.</p>
            <div class="mt-6 flex items-center justify-center gap-3">
              <button @click="showDel = false" class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
              <button @click="doDelete" :disabled="deleting" class="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60 transition-colors cursor-pointer">
                <Loader2 v-if="deleting" :size="16" class="animate-spin" /><Trash2 v-else :size="16" /> Delete
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
