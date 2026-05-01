<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import {
  HardHat, Plus, Search, Pencil, Trash2, Phone, Mail, X,
  ChevronLeft, ChevronRight, Loader2, AlertTriangle,
  CheckCircle2, XCircle, Building2, Wrench, MapPin, CreditCard,
} from '@lucide/vue';
import api from '@/lib/api';

interface Contractor {
  id: string; name: string; company_name: string; phone: string;
  email: string; specialization: string; trade_license: string;
  address: string; bank_name: string; bank_account: string;
  total_contract_amount: number; total_paid: number;
  is_active: boolean; organization_id: string; created_at: string;
}
interface Meta { page: number; per_page: number; total: number; total_pages: number; }

const contractors = ref<Contractor[]>([]);
const meta = ref<Meta>({ page: 1, per_page: 20, total: 0, total_pages: 0 });
const loading = ref(false);
const q = ref('');
const page = ref(1);
const showModal = ref(false);
const editing = ref(false);
const submitting = ref(false);
const formErr = ref('');
const showDel = ref(false);
const delTarget = ref<Contractor | null>(null);
const deleting = ref(false);

const blank = () => ({
  id: '', name: '', company_name: '', phone: '', email: '',
  specialization: '', trade_license: '', address: '',
  bank_name: '', bank_account: '',
});
const form = reactive<Record<string, string>>(blank());

const fmtCurrency = (v: number) =>
  v >= 1e7 ? `${(v / 1e7).toFixed(1)}Cr` : v >= 1e5 ? `${(v / 1e5).toFixed(1)}L` : v >= 1e3 ? `${(v / 1e3).toFixed(1)}K` : v.toLocaleString('en-BD');
const pct = (c: Contractor) => {
  const total = c.total_contract_amount || 0;
  if (!total) return 0;
  return Math.min(100, Math.round(((c.total_paid || 0) / total) * 100));
};
const pColor = (v: number) => v >= 90 ? 'bg-red-500' : v >= 70 ? 'bg-amber-500' : 'bg-emerald-500';

const stats = computed(() => {
  const totalAmt = contractors.value.reduce((s, c) => s + (c.total_contract_amount || 0), 0);
  const totalPaid = contractors.value.reduce((s, c) => s + (c.total_paid || 0), 0);
  const active = contractors.value.filter(c => c.is_active).length;
  return [
    { label: 'Total Contractors', value: meta.value.total, icon: HardHat, bg: 'bg-emerald-50', tx: 'text-emerald-600' },
    { label: 'Active', value: active, icon: CheckCircle2, bg: 'bg-blue-50', tx: 'text-blue-600' },
    { label: 'Total Contracts', value: `৳${fmtCurrency(totalAmt)}`, icon: CreditCard, bg: 'bg-purple-50', tx: 'text-purple-600' },
    { label: 'Total Paid', value: `৳${fmtCurrency(totalPaid)}`, icon: Building2, bg: 'bg-amber-50', tx: 'text-amber-600' },
  ];
});

const pages = computed(() => {
  const t = meta.value.total_pages, c = meta.value.page, r: (number | string)[] = [];
  if (t <= 5) { for (let i = 1; i <= t; i++) r.push(i); }
  else { r.push(1); if (c > 3) r.push('…'); for (let i = Math.max(2, c - 1); i <= Math.min(t - 1, c + 1); i++) r.push(i); if (c < t - 2) r.push('…'); r.push(t); }
  return r;
});

async function fetch() {
  loading.value = true;
  try {
    const p: any = { page: page.value, per_page: 20 };
    if (q.value.trim()) p.search = q.value.trim();
    const { data } = await api.get('/contractors', { params: p });
    contractors.value = data.data || [];
    meta.value = data.meta || { page: 1, per_page: 20, total: 0, total_pages: 0 };
  } catch { contractors.value = []; } finally { loading.value = false; }
}

async function submit() {
  formErr.value = '';
  if (!form.name.trim()) { formErr.value = 'Contractor name is required.'; return; }
  submitting.value = true;
  try {
    const payload: any = { ...form };
    if (editing.value) await api.put(`/contractors/${form.id}`, payload);
    else await api.post('/contractors', payload);
    showModal.value = false;
    await fetch();
  } catch (e: any) {
    formErr.value = e.response?.data?.error?.message || 'Failed to save contractor.';
  } finally { submitting.value = false; }
}

async function doDelete() {
  if (!delTarget.value) return;
  deleting.value = true;
  try {
    await api.delete(`/contractors/${delTarget.value.id}`);
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

function openEdit(c: Contractor) {
  Object.assign(form, {
    id: c.id, name: c.name, company_name: c.company_name || '',
    phone: c.phone || '', email: c.email || '', specialization: c.specialization || '',
    trade_license: c.trade_license || '', address: c.address || '',
    bank_name: c.bank_name || '', bank_account: c.bank_account || '',
  });
  editing.value = true;
  formErr.value = '';
  showModal.value = true;
}

watch(q, () => { page.value = 1; fetch(); });
watch(page, fetch);
onMounted(fetch);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <div>
        <h2 class="text-2xl font-bold text-slate-900">চুক্তিকার / Contractors</h2>
        <p class="mt-1 text-sm text-slate-500">Manage contractor information and payment tracking.</p>
      </div>
      <button @click="openCreate"
        class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 transition-colors cursor-pointer">
        <Plus :size="18" /> নতুন চুক্তিকার / Add Contractor
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

    <!-- Search -->
    <div class="flex flex-col sm:flex-row gap-3">
      <div class="relative flex-1">
        <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        <input v-model="q" type="text" placeholder="Search by name, company, specialization…"
          class="w-full rounded-lg border border-slate-200 bg-white py-2.5 pl-9 pr-3 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 :size="32" class="animate-spin text-emerald-500" />
      <span class="ml-3 text-sm text-slate-500">Loading contractors…</span>
    </div>

    <!-- Empty -->
    <div v-else-if="!contractors.length"
      class="flex flex-col items-center justify-center py-20 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <div class="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mb-4">
        <HardHat :size="32" class="text-slate-400" />
      </div>
      <h3 class="text-lg font-semibold text-slate-900">No Contractors Found</h3>
      <p class="mt-1 text-sm text-slate-500 max-w-sm text-center">
        {{ q ? 'Try adjusting your search.' : 'Get started by adding your first contractor.' }}
      </p>
      <button v-if="!q" @click="openCreate"
        class="mt-4 inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 transition-colors cursor-pointer">
        <Plus :size="16" /> Add Contractor
      </button>
    </div>

    <!-- Desktop Table -->
    <div v-if="!loading && contractors.length" class="hidden lg:block rounded-xl bg-white border border-slate-200/80 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
          <thead class="bg-slate-50/80 border-b border-slate-200">
            <tr>
              <th class="px-5 py-3 font-semibold text-slate-600">Name</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Company</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Specialization</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Phone</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Contract Amt (৳)</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Paid (৳)</th>
              <th class="px-5 py-3 font-semibold text-slate-600 min-w-[140px]">Payment</th>
              <th class="px-5 py-3 font-semibold text-slate-600">Status</th>
              <th class="px-5 py-3 font-semibold text-slate-600 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="c in contractors" :key="c.id" class="hover:bg-slate-50/60 transition-colors">
              <td class="px-5 py-3.5">
                <div class="font-medium text-slate-900 truncate max-w-[160px]">{{ c.name }}</div>
                <div v-if="c.email" class="text-xs text-slate-400 truncate max-w-[160px]">{{ c.email }}</div>
              </td>
              <td class="px-5 py-3.5">
                <span class="inline-flex items-center gap-1 text-slate-600">
                  <Building2 :size="12" class="text-slate-400 flex-shrink-0" />
                  <span class="truncate max-w-[140px]">{{ c.company_name || '—' }}</span>
                </span>
              </td>
              <td class="px-5 py-3.5">
                <span class="inline-flex items-center gap-1 text-slate-600">
                  <Wrench :size="12" class="text-slate-400 flex-shrink-0" />
                  <span class="truncate max-w-[120px]">{{ c.specialization || '—' }}</span>
                </span>
              </td>
              <td class="px-5 py-3.5 whitespace-nowrap">
                <span class="inline-flex items-center gap-1 text-slate-600">
                  <Phone :size="12" class="text-slate-400" />{{ c.phone || '—' }}
                </span>
              </td>
              <td class="px-5 py-3.5 font-medium text-slate-700 whitespace-nowrap">
                ৳{{ fmtCurrency(c.total_contract_amount || 0) }}
              </td>
              <td class="px-5 py-3.5 font-medium text-slate-700 whitespace-nowrap">
                ৳{{ fmtCurrency(c.total_paid || 0) }}
              </td>
              <td class="px-5 py-3.5">
                <div class="flex items-center gap-2">
                  <div class="flex-1 h-2 rounded-full bg-slate-100 overflow-hidden">
                    <div :class="['h-full rounded-full transition-all', pColor(pct(c))]" :style="{ width: pct(c) + '%' }"></div>
                  </div>
                  <span class="text-xs font-medium text-slate-500 w-8 text-right">{{ pct(c) }}%</span>
                </div>
              </td>
              <td class="px-5 py-3.5">
                <span :class="['inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset',
                  c.is_active ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20' : 'bg-red-50 text-red-600 ring-red-600/20']">
                  <component :is="c.is_active ? CheckCircle2 : XCircle" :size="12" />
                  {{ c.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-5 py-3.5 text-right">
                <button @click="openEdit(c)" class="p-1.5 rounded-lg text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 transition-colors cursor-pointer"><Pencil :size="16" /></button>
                <button @click="delTarget = c; showDel = true" class="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors cursor-pointer"><Trash2 :size="16" /></button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Mobile Cards -->
    <div v-if="!loading && contractors.length" class="lg:hidden space-y-3">
      <div v-for="c in contractors" :key="c.id" class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-4 space-y-3">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <h4 class="font-semibold text-slate-900 truncate">{{ c.name }}</h4>
            <p v-if="c.company_name" class="text-xs text-slate-400 truncate">{{ c.company_name }}</p>
          </div>
          <span :class="['inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset flex-shrink-0',
            c.is_active ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20' : 'bg-red-50 text-red-600 ring-red-600/20']">
            {{ c.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>
        <div class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">
          <span v-if="c.specialization" class="inline-flex items-center gap-1"><Wrench :size="12" class="text-slate-400" />{{ c.specialization }}</span>
          <span v-if="c.phone" class="inline-flex items-center gap-1"><Phone :size="12" class="text-slate-400" />{{ c.phone }}</span>
        </div>
        <div class="flex items-center justify-between text-xs text-slate-500">
          <span>৳{{ fmtCurrency(c.total_paid || 0) }} / ৳{{ fmtCurrency(c.total_contract_amount || 0) }}</span>
          <span class="font-medium text-slate-700">{{ pct(c) }}%</span>
        </div>
        <div class="h-2 rounded-full bg-slate-100 overflow-hidden">
          <div :class="['h-full rounded-full transition-all', pColor(pct(c))]" :style="{ width: pct(c) + '%' }"></div>
        </div>
        <div class="flex items-center gap-2 pt-1 border-t border-slate-100">
          <button @click="openEdit(c)" class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 transition-colors cursor-pointer"><Pencil :size="13" /> Edit</button>
          <button @click="delTarget = c; showDel = true" class="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-red-700 bg-red-50 hover:bg-red-100 transition-colors cursor-pointer"><Trash2 :size="13" /> Delete</button>
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
              <h3 class="text-lg font-semibold text-slate-900">{{ editing ? 'Edit Contractor' : 'নতুন চুক্তিকার / Add Contractor' }}</h3>
              <button @click="showModal = false" class="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"><X :size="20" /></button>
            </div>
            <form @submit.prevent="submit" class="p-6 space-y-4">
              <div v-if="formErr" class="flex items-center gap-2 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
                <AlertTriangle :size="16" class="flex-shrink-0" />{{ formErr }}
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Name <span class="text-red-500">*</span></label>
                <input v-model="form.name" type="text" required placeholder="e.g. Rahim Sheikh"
                  class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Company Name</label>
                <input v-model="form.company_name" type="text" placeholder="e.g. Rahim Construction"
                  class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1">Phone</label>
                  <input v-model="form.phone" type="tel" placeholder="+880…"
                    class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1">Email</label>
                  <input v-model="form.email" type="email" placeholder="rahim@example.com"
                    class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
                </div>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1">Specialization</label>
                  <input v-model="form.specialization" type="text" placeholder="e.g. Civil Work"
                    class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1">Trade License</label>
                  <input v-model="form.trade_license" type="text" placeholder="e.g. TL-2024-001"
                    class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Address</label>
                <input v-model="form.address" type="text" placeholder="e.g. Dhaka"
                  class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1">Bank Name</label>
                  <input v-model="form.bank_name" type="text" placeholder="e.g. Dutch-Bangla"
                    class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-700 mb-1">Bank Account</label>
                  <input v-model="form.bank_account" type="text" placeholder="e.g. 12345678"
                    class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 focus:outline-none transition" />
                </div>
              </div>
              <div class="flex items-center justify-end gap-3 pt-2">
                <button type="button" @click="showModal = false" class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
                <button type="submit" :disabled="submitting"
                  class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-emerald-700 disabled:opacity-60 transition-colors cursor-pointer">
                  <Loader2 v-if="submitting" :size="16" class="animate-spin" />{{ editing ? 'Update Contractor' : 'Create Contractor' }}
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
            <h3 class="text-lg font-semibold text-slate-900">Delete Contractor?</h3>
            <p class="mt-2 text-sm text-slate-500">Are you sure you want to delete <span class="font-medium text-slate-700">"{{ delTarget?.name }}"</span>? This action cannot be undone.</p>
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
