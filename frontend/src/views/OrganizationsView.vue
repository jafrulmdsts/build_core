<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import api from '@/lib/api';
import {
  Building2, Plus, Search, Edit, Trash2, X,
  ChevronLeft, ChevronRight, Loader2, EyeOff, Eye,
  Phone, Mail, Link, Hash,
} from '@lucide/vue';

useI18n();

interface Organization {
  id: number; name: string; slug: string; address: string | null;
  phone: string | null; email: string | null; website: string | null;
  reg_number: string | null; is_active: boolean; currency_code: string;
  timezone: string; created_at: string; logo_url?: string;
}

interface PaginationMeta { page: number; per_page: number; total: number; total_pages: number; }

const organizations = ref<Organization[]>([]);
const loading = ref(true);
const saving = ref(false);
const searchQuery = ref('');
const currentPage = ref(1);
const perPage = ref(20);
const meta = ref<PaginationMeta>({ page: 1, per_page: 20, total: 0, total_pages: 0 });
const showFormModal = ref(false);
const showDeleteDialog = ref(false);
const isEditing = ref(false);
const selectedOrg = ref<Organization | null>(null);
const errorMessage = ref('');

const defaultForm = {
  name: '', slug: '', address: '', phone: '', email: '',
  website: '', reg_number: '', currency_code: 'BDT', timezone: 'Asia/Dhaka',
};
const form = reactive({ ...defaultForm });

async function fetchOrganizations() {
  loading.value = true;
  errorMessage.value = '';
  try {
    const { data } = await api.get('/organizations', {
      params: { page: currentPage.value, per_page: perPage.value },
    });
    organizations.value = data.data || [];
    meta.value = data.meta || { page: 1, per_page: 20, total: 0, total_pages: 0 };
  } catch {
    errorMessage.value = 'Failed to load organizations. Please try again.';
  } finally {
    loading.value = false;
  }
}

async function saveOrganization() {
  if (!form.name.trim() || !form.slug.trim()) return;
  saving.value = true;
  errorMessage.value = '';
  try {
    const payload = {
      name: form.name.trim(), slug: form.slug.trim(),
      address: form.address.trim() || null, phone: form.phone.trim() || null,
      email: form.email.trim() || null, website: form.website.trim() || null,
      reg_number: form.reg_number.trim() || null,
      currency_code: form.currency_code, timezone: form.timezone,
    };
    if (isEditing.value && selectedOrg.value) {
      await api.put(`/organizations/${selectedOrg.value.id}`, payload);
    } else {
      await api.post('/organizations', payload);
    }
    closeFormModal();
    await fetchOrganizations();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error?.message || 'Failed to save organization.';
  } finally {
    saving.value = false;
  }
}

async function deleteOrganization() {
  if (!selectedOrg.value) return;
  try {
    await api.delete(`/organizations/${selectedOrg.value.id}`);
    showDeleteDialog.value = false;
    selectedOrg.value = null;
    await fetchOrganizations();
  } catch {
    errorMessage.value = 'Failed to delete organization.';
  }
}

async function toggleOrgStatus(org: Organization) {
  try {
    await api.put(`/organizations/${org.id}`, { is_active: !org.is_active });
    org.is_active = !org.is_active;
  } catch {
    errorMessage.value = 'Failed to update organization status.';
  }
}

function openCreateModal() {
  isEditing.value = false;
  selectedOrg.value = null;
  Object.assign(form, { ...defaultForm });
  errorMessage.value = '';
  showFormModal.value = true;
}

function openEditModal(org: Organization) {
  isEditing.value = true;
  selectedOrg.value = org;
  Object.assign(form, {
    name: org.name, slug: org.slug, address: org.address || '',
    phone: org.phone || '', email: org.email || '', website: org.website || '',
    reg_number: org.reg_number || '', currency_code: org.currency_code || 'BDT',
    timezone: org.timezone || 'Asia/Dhaka',
  });
  errorMessage.value = '';
  showFormModal.value = true;
}

function confirmDelete(org: Organization) { selectedOrg.value = org; showDeleteDialog.value = true; }
function closeFormModal() { showFormModal.value = false; errorMessage.value = ''; }
function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}
function autoSlug() {
  if (!isEditing.value) form.slug = form.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

const filteredOrgs = computed(() => {
  if (!searchQuery.value.trim()) return organizations.value;
  const q = searchQuery.value.toLowerCase();
  return organizations.value.filter(
    (o) => o.name.toLowerCase().includes(q) || o.slug.toLowerCase().includes(q) || (o.email || '').toLowerCase().includes(q),
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

watch(currentPage, () => fetchOrganizations());
onMounted(fetchOrganizations);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-900">সংস্থা সমূহ / Organizations</h2>
        <p class="mt-1 text-sm text-slate-500">Manage all organizations in the system.</p>
      </div>
      <button @click="openCreateModal" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 cursor-pointer">
        <Plus :size="18" /> তৈরি করুন / Create New
      </button>
    </div>

    <!-- Error Banner -->
    <div v-if="errorMessage" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 flex items-center gap-2">
      <span class="text-sm text-red-700 flex-1">{{ errorMessage }}</span>
      <button @click="errorMessage = ''" class="text-red-500 hover:text-red-700 cursor-pointer"><X :size="16" /></button>
    </div>

    <!-- Search -->
    <div class="relative">
      <Search :size="18" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
      <input v-model="searchQuery" type="text" placeholder="Search by name, slug, or email…" class="block w-full rounded-lg border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20" />
    </div>

    <!-- Loading Skeleton -->
    <div v-if="loading" class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-6">
      <div class="animate-pulse space-y-4"><div v-for="i in 5" :key="i" class="h-12 bg-slate-100 rounded-lg"></div></div>
      <div class="mt-6 flex items-center justify-center gap-2 text-sm text-slate-400">
        <Loader2 :size="16" class="animate-spin" /> Loading organizations…
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="organizations.length === 0" class="flex flex-col items-center justify-center py-20 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <div class="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mb-4"><Building2 :size="32" class="text-slate-400" /></div>
      <h3 class="text-lg font-semibold text-slate-900">No organizations found</h3>
      <p class="mt-1 text-sm text-slate-500 max-w-sm text-center">Get started by creating your first organization.</p>
      <button @click="openCreateModal" class="mt-4 inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 cursor-pointer">
        <Plus :size="16" /> তৈরি করুন / Create
      </button>
    </div>

    <!-- No Search Results -->
    <div v-else-if="filteredOrgs.length === 0 && searchQuery" class="flex flex-col items-center justify-center py-16 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <Search :size="32" class="text-slate-300 mb-3" />
      <p class="text-sm text-slate-500">No organizations match "{{ searchQuery }}"</p>
    </div>

    <!-- Data Display -->
    <template v-else>
      <!-- Table (Desktop) -->
      <div class="hidden md:block rounded-xl bg-white border border-slate-200/80 shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200">
            <thead class="bg-slate-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Name</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Slug</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Email</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Phone</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Reg #</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Created</th>
                <th class="px-6 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="org in filteredOrgs" :key="org.id" class="hover:bg-slate-50/50 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-lg bg-emerald-50 flex items-center justify-center flex-shrink-0"><Building2 :size="18" class="text-emerald-600" /></div>
                    <span class="text-sm font-medium text-slate-900">{{ org.name }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 text-sm text-slate-500 font-mono">{{ org.slug }}</td>
                <td class="px-6 py-4 text-sm text-slate-500">{{ org.email || '—' }}</td>
                <td class="px-6 py-4 text-sm text-slate-500">{{ org.phone || '—' }}</td>
                <td class="px-6 py-4">
                  <span :class="['inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium', org.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500']">
                    <span :class="['w-1.5 h-1.5 rounded-full', org.is_active ? 'bg-emerald-500' : 'bg-slate-400']"></span>
                    {{ org.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-slate-500">{{ org.reg_number || '—' }}</td>
                <td class="px-6 py-4 text-sm text-slate-500">{{ formatDate(org.created_at) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right">
                  <div class="flex items-center justify-end gap-1">
                    <button @click="openEditModal(org)" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer" title="Edit"><Edit :size="16" /></button>
                    <button @click="toggleOrgStatus(org)" :class="['rounded-lg p-2 transition-colors cursor-pointer', org.is_active ? 'text-slate-400 hover:bg-slate-100 hover:text-amber-600' : 'text-slate-400 hover:bg-slate-100 hover:text-emerald-600']" :title="org.is_active ? 'Deactivate' : 'Activate'">
                      <EyeOff v-if="org.is_active" :size="16" /><Eye v-else :size="16" />
                    </button>
                    <button @click="confirmDelete(org)" class="rounded-lg p-2 text-slate-400 hover:bg-red-50 hover:text-red-600 transition-colors cursor-pointer" title="Delete"><Trash2 :size="16" /></button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
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
        <div v-for="org in filteredOrgs" :key="org.id" class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-4 space-y-3">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center flex-shrink-0"><Building2 :size="20" class="text-emerald-600" /></div>
              <div>
                <p class="text-sm font-semibold text-slate-900">{{ org.name }}</p>
                <p class="text-xs text-slate-400 font-mono">{{ org.slug }}</p>
              </div>
            </div>
            <span :class="['inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium', org.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500']">
              <span :class="['w-1.5 h-1.5 rounded-full', org.is_active ? 'bg-emerald-500' : 'bg-slate-400']"></span>
              {{ org.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div class="grid grid-cols-2 gap-2 text-xs text-slate-500">
            <div v-if="org.email" class="flex items-center gap-1.5"><Mail :size="12" class="text-slate-400" />{{ org.email }}</div>
            <div v-if="org.phone" class="flex items-center gap-1.5"><Phone :size="12" class="text-slate-400" />{{ org.phone }}</div>
            <div v-if="org.reg_number" class="flex items-center gap-1.5"><Hash :size="12" class="text-slate-400" />{{ org.reg_number }}</div>
            <div class="flex items-center gap-1.5">{{ formatDate(org.created_at) }}</div>
          </div>
          <div class="flex items-center gap-2 pt-1 border-t border-slate-100">
            <button @click="openEditModal(org)" class="flex-1 flex items-center justify-center gap-1.5 rounded-lg border border-slate-200 py-2 text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer"><Edit :size="13" /> Edit</button>
            <button @click="toggleOrgStatus(org)" class="flex-1 flex items-center justify-center gap-1.5 rounded-lg border py-2 text-xs font-medium transition-colors cursor-pointer" :class="org.is_active ? 'border-amber-200 text-amber-600 hover:bg-amber-50' : 'border-emerald-200 text-emerald-600 hover:bg-emerald-50'">
              <EyeOff v-if="org.is_active" :size="13" /><Eye v-else :size="13" /> {{ org.is_active ? 'Deactivate' : 'Activate' }}
            </button>
            <button @click="confirmDelete(org)" class="flex items-center justify-center rounded-lg border border-red-200 px-3 py-2 text-xs font-medium text-red-600 hover:bg-red-50 transition-colors cursor-pointer"><Trash2 :size="13" /></button>
          </div>
        </div>
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
        <div class="relative w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-2xl bg-white shadow-2xl">
          <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 sticky top-0 bg-white rounded-t-2xl z-10">
            <h3 class="text-lg font-semibold text-slate-900">{{ isEditing ? 'Edit Organization' : 'তৈরি করুন / Create Organization' }}</h3>
            <button @click="closeFormModal" class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer"><X :size="20" /></button>
          </div>
          <form @submit.prevent="saveOrganization" class="p-6 space-y-4">
            <div v-if="errorMessage" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">{{ errorMessage }}</div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Name <span class="text-red-500">*</span></label>
              <div class="relative">
                <Building2 :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input v-model="form.name" @input="autoSlug" type="text" required placeholder="e.g. ABC Construction Ltd." :class="inputIconCls" />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Slug <span class="text-red-500">*</span></label>
              <input v-model="form.slug" type="text" required placeholder="abc-construction" :class="[inputCls, 'font-mono']" :readonly="isEditing" />
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Email</label>
                <div class="relative"><Mail :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="form.email" type="email" placeholder="org@example.com" :class="inputIconCls" /></div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Phone</label>
                <div class="relative"><Phone :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="form.phone" type="tel" placeholder="+880 1XXX-XXXXXX" :class="inputIconCls" /></div>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Website</label>
                <div class="relative"><Link :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="form.website" type="url" placeholder="https://example.com" :class="inputIconCls" /></div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Reg Number</label>
                <div class="relative"><Hash :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="form.reg_number" type="text" placeholder="REG-12345" :class="inputIconCls" /></div>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Currency</label>
                <select v-model="form.currency_code" :class="inputCls + ' cursor-pointer'">
                  <option value="BDT">BDT (৳)</option><option value="USD">USD ($)</option><option value="EUR">EUR (€)</option><option value="GBP">GBP (£)</option><option value="INR">INR (₹)</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Timezone</label>
                <select v-model="form.timezone" :class="inputCls + ' cursor-pointer'">
                  <option value="Asia/Dhaka">Asia/Dhaka (BST +6)</option><option value="Asia/Kolkata">Asia/Kolkata (IST +5:30)</option><option value="UTC">UTC</option><option value="America/New_York">America/New_York</option><option value="Europe/London">Europe/London</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Address</label>
              <textarea v-model="form.address" rows="2" placeholder="Enter organization address" class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 resize-none"></textarea>
            </div>
            <div class="flex items-center justify-end gap-3 pt-2">
              <button type="button" @click="closeFormModal" class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
              <button type="submit" :disabled="saving" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer">
                <Loader2 v-if="saving" :size="16" class="animate-spin" />{{ isEditing ? 'Update' : 'Create' }}
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
          <h3 class="text-lg font-semibold text-slate-900">Delete Organization?</h3>
          <p class="mt-2 text-sm text-slate-500">Are you sure you want to delete <strong class="text-slate-700">{{ selectedOrg?.name }}</strong>? This action cannot be undone.</p>
          <div class="mt-6 flex items-center gap-3">
            <button @click="showDeleteDialog = false" class="flex-1 rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
            <button @click="deleteOrganization" class="flex-1 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-700 transition-colors cursor-pointer">Delete</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
