<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import {
  Receipt, Plus, Search, Pencil, Trash2, X, CalendarDays,
  ChevronLeft, ChevronRight, Loader2, AlertTriangle,
  CheckCircle2, Clock, DollarSign, CreditCard, Wallet, Banknote, Landmark,
} from '@lucide/vue';
import api from '@/lib/api';

interface Expense {
  id: string; project_id: string; project_name: string;
  category: string; amount: number; description: string;
  expense_date: string; vendor: string; payment_method: string;
  status: string; receipt_url: string | null;
  created_by: string; organization_id: string; created_at: string;
}
interface Project { id: string; name: string; }
interface Meta { page: number; per_page: number; total: number; total_pages: number; }

const CATEGORY_OPT = [
  { v: '', l: 'All Categories' }, { v: 'materials', l: 'Materials' },
  { v: 'labor', l: 'Labor' }, { v: 'equipment', l: 'Equipment' },
  { v: 'transport', l: 'Transport' }, { v: 'food', l: 'Food' },
  { v: 'rent', l: 'Rent' }, { v: 'utilities', l: 'Utilities' },
  { v: 'other', l: 'Other' },
];
const PAY_METHODS: Record<string, string> = {
  bank_transfer: 'Bank Transfer', cash: 'Cash',
  mobile_banking: 'Mobile Banking', cheque: 'Cheque',
};
const PAY_ICONS: Record<string, any> = {
  bank_transfer: Landmark, cash: Banknote, mobile_banking: Wallet, cheque: CreditCard,
};
const CAT_STYLES: Record<string, { bg: string; tx: string }> = {
  materials:   { bg: 'bg-blue-50',    tx: 'text-blue-700' },
  labor:       { bg: 'bg-amber-50',   tx: 'text-amber-700' },
  equipment:   { bg: 'bg-purple-50',  tx: 'text-purple-700' },
  transport:   { bg: 'bg-cyan-50',    tx: 'text-cyan-700' },
  food:        { bg: 'bg-orange-50',  tx: 'text-orange-700' },
  rent:        { bg: 'bg-rose-50',    tx: 'text-rose-700' },
  utilities:   { bg: 'bg-teal-50',    tx: 'text-teal-700' },
  other:       { bg: 'bg-slate-50',   tx: 'text-slate-600' },
};
const ST_STYLES: Record<string, { bg: string; tx: string; ic: any; l: string }> = {
  approved:  { bg: 'bg-emerald-50 ring-emerald-600/20', tx: 'text-emerald-700', ic: CheckCircle2, l: 'Approved' },
  pending:   { bg: 'bg-amber-50 ring-amber-600/20',     tx: 'text-amber-700',   ic: Clock,        l: 'Pending' },
  rejected:  { bg: 'bg-red-50 ring-red-600/20',         tx: 'text-red-700',     ic: X,            l: 'Rejected' },
};

const expenses = ref<Expense[]>([]);
const projects = ref<Project[]>([]);
const meta = ref<Meta>({ page: 1, per_page: 20, total: 0, total_pages: 0 });
const loading = ref(false);
const q = ref('');
const catFilter = ref('');
const page = ref(1);
const showModal = ref(false);
const editing = ref(false);
const submitting = ref(false);
const formErr = ref('');
const showDel = ref(false);
const delTarget = ref<Expense | null>(null);
const deleting = ref(false);

const blank = () => ({
  id: '', project_id: '', category: '', amount: '', description: '',
  expense_date: '', vendor: '', payment_method: '',
});
const form = reactive<Record<string, string>>(blank());

const fmtCurrency = (v: number) =>
  v >= 1e7 ? `${(v / 1e7).toFixed(1)}Cr` : v >= 1e5 ? `${(v / 1e5).toFixed(1)}L` : v >= 1e3 ? `${(v / 1e3).toFixed(1)}K` : v.toLocaleString('en-BD');
const fmtDate = (d: string) => d ? new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : '—';
const catLabel = (v: string) => CATEGORY_OPT.find(c => c.v === v)?.l || v;
const payLabel = (v: string) => PAY_METHODS[v] || v;
const stStyle = (v: string) => ST_STYLES[v] || { bg: 'bg-slate-50 ring-slate-500/20', tx: 'text-slate-600', ic: Clock, l: v };
const catStyle = (v: string) => CAT_STYLES[v] || { bg: 'bg-slate-50', tx: 'text-slate-600' };

const stats = computed(() => {
  const totalAmt = expenses.value.reduce((s, e) => s + (e.amount || 0), 0);
  const now = new Date();
  const thisMonth = expenses.value.filter(e => {
    const d = new Date(e.expense_date || e.created_at);
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
  }).reduce((s, e) => s + (e.amount || 0), 0);
  const pending = expenses.value.filter(e => e.status === 'pending').reduce((s, e) => s + (e.amount || 0), 0);
  const approved = expenses.value.filter(e => e.status === 'approved').reduce((s, e) => s + (e.amount || 0), 0);
  return [
    { label: 'Total Expenses', value: `৳${fmtCurrency(totalAmt)}`, icon: DollarSign, bg: 'bg-emerald-50', tx: 'text-emerald-600' },
    { label: 'This Month', value: `৳${fmtCurrency(thisMonth)}`, icon: CalendarDays, bg: 'bg-blue-50', tx: 'text-blue-600' },
    { label: 'Pending Approval', value: `৳${fmtCurrency(pending)}`, icon: Clock, bg: 'bg-amber-50', tx: 'text-amber-600' },
    { label: 'Approved', value: `৳${fmtCurrency(approved)}`, icon: CheckCircle2, bg: 'bg-purple-50', tx: 'text-purple-600' },
  ];
});

const pages = computed(() => {
  const t = meta.value.total_pages, c = meta.value.page, r: (number | string)[] = [];
  if (t <= 5) { for (let i = 1; i <= t; i++) r.push(i); }
  else { r.push(1); if (c > 3) r.push('…'); for (let i = Math.max(2, c - 1); i <= Math.min(t - 1, c + 1); i++) r.push(i); if (c < t - 2) r.push('…'); r.push(t); }
  return r;
});

async function fetchProjects() {
  try {
    const { data } = await api.get('/projects', { params: { per_page: 100 } });
    projects.value = (data.data || []).map((p: any) => ({ id: p.id, name: p.name }));
  } catch { projects.value = []; }
}

async function fetch() {
  loading.value = true;
  try {
    const p: any = { page: page.value, per_page: 20 };
    if (q.value.trim()) p.search = q.value.trim();
    if (catFilter.value) p.category = catFilter.value;
    const { data } = await api.get('/expenses', { params: p });
    expenses.value = data.data || [];
    meta.value = data.meta || { page: 1, per_page: 20, total: 0, total_pages: 0 };
  } catch { expenses.value = []; } finally { loading.value = false; }
}

async function submit() {
  formErr.value = '';
  if (!form.project_id) { formErr.value = 'Project is required.'; return; }
  if (!form.category) { formErr.value = 'Category is required.'; return; }
  if (!form.amount || Number(form.amount) <= 0) { formErr.value = 'Valid amount is required.'; return; }
  if (!form.expense_date) { formErr.value = 'Expense date is required.'; return; }
  submitting.value = true;
  try {
    const payload: any = {
      project_id: form.project_id, category: form.category,
      amount: Number(form.amount), description: form.description || '',
      expense_date: form.expense_date, vendor: form.vendor || '',
      payment_method: form.payment_method || 'cash',
    };
    if (editing.value) await api.put(`/expenses/${form.id}`, payload);
    else await api.post('/expenses', payload);
    showModal.value = false;
    await fetch();
  } catch (e: any) {
    formErr.value = e.response?.data?.error?.message || 'Failed to save expense.';
  } finally { submitting.value = false; }
}

async function doDelete() {
  if (!delTarget.value) return;
  deleting.value = true;
  try {
    await api.delete(`/expenses/${delTarget.value.id}`);
    showDel.value = false;
    delTarget.value = null;
    await fetch();
  } catch {} finally { deleting.value = false; }
}

function openCreate() {
  Object.assign(form, blank());
  editing.value = false;
  formErr.value = '';
  showModal.value = true;
}

function openEdit(e: Expense) {
  Object.assign(form, {
    id: e.id, project_id: e.project_id, category: e.category,
    amount: String(e.amount), description: e.description || '',
    expense_date: e.expense_date || '', vendor: e.vendor || '',
    payment_method: e.payment_method || '',
  });
  editing.value = true;
  formErr.value = '';
  showModal.value = true;
}

watch([q, catFilter], () => { page.value = 1; fetch(); });
watch(page, fetch);
onMounted(() => { fetch(); fetchProjects(); });
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <div>
        <h2 class="text-2xl font-bold text-slate-900">ব্যয় / Expenses</h2>
        <p class="mt-1 text-sm text-slate-500">Track and manage all project expenses.</p>
      </div>
      <button @click="openCreate"
        class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 transition-colors cursor-pointer">
        <Plus :size="18" /> নতুন ব্যয় / Add Expense
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      <div v-for="s in stats" :key="s.label"
        class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-4 sm:p-5 hover:shadow-md transition-shadow">
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
        <input v-model="q" type="text" placeholder="Search by project, vendor, description…"
          class="w-full rounded-lg border border-slate-200 bg-white py-2.5 pl-9 pr-3 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
      </div>
      <select v-model="catFilter"
        class="rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-700 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition cursor-pointer">
        <option v-for="o in CATEGORY_OPT" :key="o.v" :value="o.v">{{ o.l }}</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 :size="32" class="animate-spin text-emerald-500" />
      <span class="ml-3 text-sm text-slate-500">Loading expenses…</span>
    </div>

    <!-- Empty -->
    <div v-else-if="!expenses.length"
      class="flex flex-col items-center justify-center py-20 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <div class="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mb-4">
        <Receipt :size="32" class="text-slate-400" />
      </div>
      <h3 class="text-lg font-semibold text-slate-900">No Expenses Found</h3>
      <p class="mt-1 text-sm text-slate-500 max-w-sm text-center">
        {{ q || catFilter ? 'Try adjusting your search or filter.' : 'Get started by recording your first expense.' }}
      </p>
      <button v-if="!q && !catFilter" @click="openCreate"
        class="mt-4 inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 transition-colors cursor-pointer">
        <Plus :size="16" /> Add Expense
      </button>
    </div>

    <!-- Desktop Table -->
    <div v-if="!loading && expenses.length" class="hidden lg:block rounded-xl bg-white border border-slate-200/80 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
          <thead class="bg-slate-50/80 border-b border-slate-200">
            <tr>
              <th class="px-5 py-3 font-semibold text-slate-600">Project</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Category</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Amount (৳)</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Vendor</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Date</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Payment Method</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Status</th>
              <th class="px-5 py-3 font-semibold text-slate-600 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="e in expenses" :key="e.id" class="hover:bg-slate-50/60 transition-colors">
              <td class="px-5 py-3.5">
                <div class="font-medium text-slate-900 truncate max-w-[160px]">{{ e.project_name || '—' }}</div>
              </td>
              <td class="px-5 py-3.5">
                <span :class="['inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium', catStyle(e.category).bg, catStyle(e.category).tx]">
                  {{ catLabel(e.category) }}
                </span>
              </td>
              <td class="px-5 py-3.5 font-semibold text-slate-800 whitespace-nowrap">
                ৳{{ fmtCurrency(e.amount || 0) }}
              </td>
              <td class="px-5 py-3.5">
                <span class="truncate max-w-[140px] block text-slate-600">{{ e.vendor || '—' }}</span>
              </td>
              <td class="px-5 py-3.5 whitespace-nowrap">
                <span class="inline-flex items-center gap-1 text-slate-600">
                  <CalendarDays :size="12" class="text-slate-400" />{{ fmtDate(e.expense_date) }}
                </span>
              </td>
              <td class="px-5 py-3.5">
                <span class="inline-flex items-center gap-1.5 text-slate-600">
                  <component :is="PAY_ICONS[e.payment_method] || CreditCard" :size="13" class="text-slate-400" />
                  {{ payLabel(e.payment_method) }}
                </span>
              </td>
              <td class="px-5 py-3.5">
                <span :class="['inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset', stStyle(e.status).bg, stStyle(e.status).tx]">
                  <component :is="stStyle(e.status).ic" :size="12" />{{ stStyle(e.status).l }}
                </span>
              </td>
              <td class="px-5 py-3.5 text-right">
                <button @click="openEdit(e)" class="p-1.5 rounded-lg text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 transition-colors cursor-pointer"><Pencil :size="16" /></button>
                <button @click="delTarget = e; showDel = true" class="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors cursor-pointer"><Trash2 :size="16" /></button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Mobile Cards -->
    <div v-if="!loading && expenses.length" class="lg:hidden space-y-3">
      <div v-for="e in expenses" :key="e.id" class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-4 space-y-3">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <h4 class="font-semibold text-slate-900 truncate">{{ e.project_name || 'Unknown Project' }}</h4>
            <p v-if="e.description" class="text-xs text-slate-400 truncate">{{ e.description }}</p>
          </div>
          <span :class="['inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset flex-shrink-0', stStyle(e.status).bg, stStyle(e.status).tx]">
            <component :is="stStyle(e.status).ic" :size="12" />{{ stStyle(e.status).l }}
          </span>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <span :class="['inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium', catStyle(e.category).bg, catStyle(e.category).tx]">
            {{ catLabel(e.category) }}
          </span>
          <span class="inline-flex items-center gap-1 text-xs text-slate-500">
            <component :is="PAY_ICONS[e.payment_method] || CreditCard" :size="11" class="text-slate-400" />{{ payLabel(e.payment_method) }}
          </span>
        </div>
        <div class="flex items-center justify-between text-xs text-slate-500">
          <span class="inline-flex items-center gap-1"><CalendarDays :size="12" class="text-slate-400" />{{ fmtDate(e.expense_date) }}</span>
          <span v-if="e.vendor" class="truncate max-w-[120px] text-slate-500">{{ e.vendor }}</span>
        </div>
        <div class="text-lg font-bold text-slate-900">৳{{ fmtCurrency(e.amount || 0) }}</div>
        <div class="flex items-center gap-2 pt-1 border-t border-slate-100">
          <button @click="openEdit(e)" class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 transition-colors cursor-pointer"><Pencil :size="13" /> Edit</button>
          <button @click="delTarget = e; showDel = true" class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-red-700 bg-red-50 hover:bg-red-100 transition-colors cursor-pointer"><Trash2 :size="13" /> Delete</button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="meta.total_pages > 1" class="flex items-center justify-between">
      <p class="text-sm text-slate-500">Showing {{ (meta.page - 1) * meta.per_page + 1 }}–{{ Math.min(meta.page * meta.per_page, meta.total) }} of {{ meta.total }}</p>
      <nav class="flex items-center gap-1">
        <button @click="page = meta.page - 1" :disabled="meta.page <= 1"
          class="p-2 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors cursor-pointer">
          <ChevronLeft :size="18" />
        </button>
        <button v-for="pg in pages" :key="pg" @click="typeof pg === 'number' && (page = pg)" :disabled="typeof pg !== 'number'"
          :class="['w-9 h-9 rounded-lg text-sm font-medium transition-colors cursor-pointer',
            pg === meta.page ? 'bg-emerald-600 text-white' : typeof pg === 'number' ? 'text-slate-600 hover:bg-slate-100' : 'text-slate-400 cursor-default']">
          {{ pg }}
        </button>
        <button @click="page = meta.page + 1" :disabled="meta.page >= meta.total_pages"
          class="p-2 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors cursor-pointer">
          <ChevronRight :size="18" />
        </button>
      </nav>
    </div>

    <!-- Create / Edit Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showModal = false"></div>
          <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 sticky top-0 bg-white rounded-t-2xl z-10">
              <h3 class="text-lg font-semibold text-slate-900">{{ editing ? 'Edit Expense' : 'নতুন ব্যয় / Add Expense' }}</h3>
              <button @click="showModal = false" class="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"><X :size="20" /></button>
            </div>
            <form @submit.prevent="submit" class="p-6 space-y-4">
              <div v-if="formErr" class="flex items-center gap-2 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
                <AlertTriangle :size="16" class="flex-shrink-0" />{{ formErr }}
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Project <span class="text-red-500">*</span></label>
                <select v-model="form.project_id" required
                  class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition cursor-pointer">
                  <option value="" disabled>Select a project</option>
                  <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
                </select>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1">Category <span class="text-red-500">*</span></label>
                  <select v-model="form.category" required
                    class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition cursor-pointer">
                    <option value="" disabled>Select category</option>
                    <option v-for="o in CATEGORY_OPT.filter(c => c.v)" :key="o.v" :value="o.v">{{ o.l }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1">Amount (৳) <span class="text-red-500">*</span></label>
                  <input v-model="form.amount" type="number" required min="1" step="1" placeholder="e.g. 50000"
                    class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Description</label>
                <textarea v-model="form.description" rows="2" placeholder="Brief description of the expense…"
                  class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition resize-none"></textarea>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Expense Date <span class="text-red-500">*</span></label>
                <input v-model="form.expense_date" type="date" required
                  class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1">Vendor</label>
                  <input v-model="form.vendor" type="text" placeholder="e.g. ABC Materials Ltd"
                    class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1">Payment Method</label>
                  <select v-model="form.payment_method"
                    class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition cursor-pointer">
                    <option value="">Select method</option>
                    <option v-for="(label, key) in PAY_METHODS" :key="key" :value="key">{{ label }}</option>
                  </select>
                </div>
              </div>
              <div class="flex items-center justify-end gap-3 pt-2">
                <button type="button" @click="showModal = false" class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
                <button type="submit" :disabled="submitting"
                  class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-emerald-700 disabled:opacity-60 transition-colors cursor-pointer">
                  <Loader2 v-if="submitting" :size="16" class="animate-spin" />{{ editing ? 'Update Expense' : 'Create Expense' }}
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
            <div class="mx-auto w-12 h-12 rounded-full bg-red-50 flex items-center justify-center mb-4">
              <AlertTriangle :size="24" class="text-red-600" />
            </div>
            <h3 class="text-lg font-semibold text-slate-900">Delete Expense?</h3>
            <p class="mt-2 text-sm text-slate-500">Are you sure you want to delete this expense of <span class="font-medium text-slate-700">৳{{ fmtCurrency(delTarget?.amount || 0) }}</span> for <span class="font-medium text-slate-700">{{ delTarget?.project_name }}</span>? This action cannot be undone.</p>
            <div class="mt-6 flex items-center justify-center gap-3">
              <button @click="showDel = false" class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
              <button @click="doDelete" :disabled="deleting"
                class="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60 transition-colors cursor-pointer">
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
