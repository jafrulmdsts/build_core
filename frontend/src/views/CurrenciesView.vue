<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/features/auth/store';
import {
  Coins, Plus, Search, Edit, Trash2, X, ChevronLeft, ChevronRight,
  Loader2, DollarSign
} from '@lucide/vue';
import api from '@/lib/api';

const { locale } = useI18n();
const isBangla = computed(() => locale.value === 'bn');
const authStore = useAuthStore();

interface Currency {
  id: string; code: string; name: string; symbol: string;
  exchange_rate: number; is_active: boolean; created_at: string;
}

const currencies = ref<Currency[]>([]);
const loading = ref(true);
const searchQuery = ref('');
const currentPage = ref(1);
const totalPages = ref(1);
const total = ref(0);
const perPage = 20;
const error = ref<string | null>(null);

const showModal = ref(false);
const isEditing = ref(false);
const editId = ref('');
const formSaving = ref(false);
const form = reactive({ code: '', name: '', symbol: '', exchange_rate: 1.0 });

const deleteModal = ref(false);
const deleteId = ref('');
const deleteName = ref('');
const deleteSaving = ref(false);

const filteredCurrencies = computed(() => {
  if (!searchQuery.value) return currencies.value;
  const q = searchQuery.value.toLowerCase();
  return currencies.value.filter(
    (c) => c.code.toLowerCase().includes(q) || c.name.toLowerCase().includes(q)
  );
});

async function fetchCurrencies() {
  loading.value = true;
  try {
    const { data } = await api.get('/currencies', { params: { page: currentPage.value, per_page } });
    currencies.value = data.data || [];
    total.value = data.meta?.total || 0;
    totalPages.value = data.meta?.total_pages || 1;
  } catch { currencies.value = []; } finally { loading.value = false; }
}

function openCreate() {
  isEditing.value = false;
  Object.assign(form, { code: '', name: '', symbol: '', exchange_rate: 1.0 });
  showModal.value = true;
}

function openEdit(c: Currency) {
  isEditing.value = true;
  editId.value = c.id;
  Object.assign(form, { code: c.code, name: c.name, symbol: c.symbol, exchange_rate: c.exchange_rate });
  showModal.value = true;
}

async function handleSubmit() {
  if (!form.code || !form.name) return;
  formSaving.value = true;
  error.value = null;
  try {
    if (isEditing.value) {
      await api.put(`/currencies/${editId.value}`, form);
    } else {
      await api.post('/currencies', form);
    }
    showModal.value = false;
    await fetchCurrencies();
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Operation failed';
  } finally { formSaving.value = false; }
}

function openDelete(c: Currency) {
  deleteId.value = c.id;
  deleteName.value = `${c.code} (${c.name})`;
  deleteModal.value = true;
}

async function handleDelete() {
  deleteSaving.value = true;
  try {
    await api.delete(`/currencies/${deleteId.value}`);
    deleteModal.value = false;
    await fetchCurrencies();
  } catch {} finally { deleteSaving.value = false; }
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

watch(searchQuery, () => { currentPage.value = 1; });
watch(currentPage, fetchCurrencies);
onMounted(fetchCurrencies);
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-900">{{ isBangla ? 'মুদ্রা' : 'Currencies' }}</h2>
        <p class="mt-1 text-sm text-slate-500">{{ isBangla ? 'মুদ্রা পরিচালনা করুন' : 'Manage currencies' }}</p>
      </div>
      <button v-if="authStore.isSuperAdmin" @click="openCreate"
        class="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 cursor-pointer">
        <Plus :size="16" /> {{ isBangla ? 'নতুন মুদ্রা' : 'Add Currency' }}
      </button>
    </div>

    <div class="relative max-w-sm">
      <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
      <input v-model="searchQuery" type="text" :placeholder="isBangla ? 'কোড, নাম খুঁজুন...' : 'Search code, name...'"
        class="w-full rounded-lg border border-slate-300 bg-white py-2 pl-9 pr-3 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20" />
    </div>

    <!-- Error -->
    <div v-if="error" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 flex items-center justify-between">
      <p class="text-sm text-red-700">{{ error }}</p>
      <button @click="error = null" class="text-red-500 hover:text-red-700 cursor-pointer"><X :size="16" /></button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 :size="32" class="animate-spin text-emerald-600" />
    </div>

    <!-- Empty -->
    <div v-else-if="currencies.length === 0" class="flex flex-col items-center justify-center py-20 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <DollarSign :size="48" class="text-slate-300 mb-4" />
      <h3 class="text-lg font-semibold text-slate-900">{{ isBangla ? 'কোন মুদ্রা নেই' : 'No Currencies Found' }}</h3>
    </div>

    <!-- Desktop Table -->
    <div v-if="filteredCurrencies.length > 0 && !loading" class="rounded-xl bg-white border border-slate-200/80 shadow-sm overflow-hidden hidden lg:block">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 border-b border-slate-200">
          <tr>
            <th class="px-4 py-3 text-left font-medium text-slate-500">Code</th>
            <th class="px-4 py-3 text-left font-medium text-slate-500">{{ isBangla ? 'নাম' : 'Name' }}</th>
            <th class="px-4 py-3 text-left font-medium text-slate-500">Symbol</th>
            <th class="px-4 py-3 text-left font-medium text-slate-500">Rate</th>
            <th class="px-4 py-3 text-left font-medium text-slate-500">{{ isBangla ? 'অবস্থা' : 'Status' }}</th>
            <th class="px-4 py-3 text-left font-medium text-slate-500">{{ isBangla ? 'কার্যক্রম' : 'Actions' }}</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="c in filteredCurrencies" :key="c.id" class="hover:bg-slate-50/50">
            <td class="px-4 py-3"><span class="inline-flex px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-xs font-mono font-semibold">{{ c.code }}</span></td>
            <td class="px-4 py-3 font-medium text-slate-900">{{ c.name }}</td>
            <td class="px-4 py-3 text-slate-600">{{ c.symbol }}</td>
            <td class="px-4 py-3 text-slate-600 font-mono">{{ c.exchange_rate.toFixed(2) }}</td>
            <td class="px-4 py-3">
              <span :class="['inline-flex px-2 py-0.5 rounded-full text-xs font-medium', c.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500']">
                {{ c.is_active ? (isBangla ? 'সক্রিয়' : 'Active') : (isBangla ? 'নিষ্ক্রিয়' : 'Inactive') }}
              </span>
            </td>
            <td class="px-4 py-3">
              <div class="flex gap-1" v-if="authStore.isSuperAdmin">
                <button @click="openEdit(c)" class="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500 hover:text-emerald-600 cursor-pointer"><Edit :size="14" /></button>
                <button @click="openDelete(c)" class="p-1.5 rounded-lg hover:bg-red-50 text-slate-500 hover:text-red-600 cursor-pointer"><Trash2 :size="14" /></button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile Cards -->
    <div v-if="filteredCurrencies.length > 0 && !loading" class="space-y-3 lg:hidden">
      <div v-for="c in filteredCurrencies" :key="c.id" class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-4">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <span class="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-xs font-mono font-semibold">{{ c.code }}</span>
            <span class="font-medium text-slate-900">{{ c.name }}</span>
          </div>
          <span :class="['px-2 py-0.5 rounded-full text-xs font-medium', c.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500']">
            {{ c.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>
        <div class="flex gap-4 text-sm text-slate-500 mb-3">
          <span>{{ c.symbol }}</span>
          <span>Rate: {{ c.exchange_rate.toFixed(2) }}</span>
        </div>
        <div v-if="authStore.isSuperAdmin" class="flex gap-2 border-t border-slate-100 pt-3">
          <button @click="openEdit(c)" class="flex items-center gap-1 text-xs text-slate-600 hover:text-emerald-600 cursor-pointer"><Edit :size="12" /> Edit</button>
          <button @click="openDelete(c)" class="flex items-center gap-1 text-xs text-red-500 hover:text-red-700 cursor-pointer"><Trash2 :size="12" /> Delete</button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && totalPages > 1" class="flex items-center justify-between">
      <p class="text-sm text-slate-500">{{ (currentPage - 1) * perPage + 1 }}–{{ Math.min(currentPage * perPage, total) }} of {{ total }}</p>
      <div class="flex items-center gap-1">
        <button @click="currentPage = Math.max(1, currentPage - 1)" :disabled="currentPage === 1" class="p-2 rounded-lg hover:bg-slate-100 disabled:opacity-40 cursor-pointer"><ChevronLeft :size="16" /></button>
        <button v-for="p in pageNumbers" :key="p" @click="typeof p === 'number' && (currentPage = p)"
          :class="['px-3 py-1.5 rounded-lg text-sm font-medium cursor-pointer', currentPage === p ? 'bg-emerald-600 text-white' : 'hover:bg-slate-100 text-slate-600']">{{ p }}</button>
        <button @click="currentPage = Math.min(totalPages, currentPage + 1)" :disabled="currentPage === totalPages" class="p-2 rounded-lg hover:bg-slate-100 disabled:opacity-40 cursor-pointer"><ChevronRight :size="16" /></button>
      </div>
    </div>
  </div>

  <!-- Create/Edit Modal -->
  <Teleport to="body">
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @click.self="showModal = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h3 class="text-base font-semibold text-slate-900">{{ isEditing ? 'Edit Currency' : 'Add Currency' }}</h3>
          <button @click="showModal = false" class="text-slate-400 hover:text-slate-600 cursor-pointer"><X :size="18" /></button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Code <span class="text-red-500">*</span></label>
            <input v-model="form.code" maxlength="3" class="w-full rounded-lg border border-slate-300 py-2 px-3 text-sm font-mono uppercase focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20" placeholder="BDT" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Name <span class="text-red-500">*</span></label>
            <input v-model="form.name" class="w-full rounded-lg border border-slate-300 py-2 px-3 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20" placeholder="Bangladeshi Taka" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Symbol</label>
              <input v-model="form.symbol" maxlength="5" class="w-full rounded-lg border border-slate-300 py-2 px-3 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20" placeholder="৳" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Exchange Rate</label>
              <input v-model.number="form.exchange_rate" type="number" step="0.01" class="w-full rounded-lg border border-slate-300 py-2 px-3 text-sm font-mono focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20" />
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-3 px-6 py-4 border-t border-slate-100">
          <button @click="showModal = false" class="px-4 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 cursor-pointer">{{ isBangla ? 'বাতিল' : 'Cancel' }}</button>
          <button @click="handleSubmit" :disabled="formSaving" class="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60 cursor-pointer">
            <Loader2 v-if="formSaving" :size="14" class="animate-spin" />
            {{ isEditing ? 'Update' : 'Create' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Delete Modal -->
  <Teleport to="body">
    <div v-if="deleteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @click.self="deleteModal = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm p-6 text-center">
        <div class="mx-auto w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mb-4"><Trash2 :size="24" class="text-red-600" /></div>
        <h3 class="text-base font-semibold text-slate-900 mb-1">{{ isBangla ? 'মুছে ফেলুন?' : 'Delete Currency?' }}</h3>
        <p class="text-sm text-slate-500 mb-6">{{ deleteName }}</p>
        <div class="flex justify-center gap-3">
          <button @click="deleteModal = false" class="px-4 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 cursor-pointer">{{ isBangla ? 'বাতিল' : 'Cancel' }}</button>
          <button @click="handleDelete" :disabled="deleteSaving" class="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-600 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60 cursor-pointer">
            <Loader2 v-if="deleteSaving" :size="14" class="animate-spin" /> Delete
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
