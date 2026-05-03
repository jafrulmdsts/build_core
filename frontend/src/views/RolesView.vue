<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import api from '@/lib/api';
import { useAuthStore } from '@/features/auth/store';
import {
  Shield, Plus, Search, Edit, Trash2, X, Loader2,
  ChevronLeft, ChevronRight, ShieldCheck, Lock, Building2,
} from '@lucide/vue';

const authStore = useAuthStore();
const isSuperAdminNoOrg = computed(() => authStore.isSuperAdmin && !authStore.hasOrganization);

interface RoleItem {
  id: string; name: string; description: string;
  permissions: string[]; is_system_role: boolean;
  is_active: boolean; organization_id: string | null; created_at: string;
}
interface PaginationMeta { page: number; per_page: number; total: number; total_pages: number; }

const PERMISSION_GROUPS = [
  { resource: 'Projects', prefix: 'projects', perms: ['read', 'write', 'delete'] },
  { resource: 'Employees', prefix: 'employees', perms: ['read', 'write', 'delete'] },
  { resource: 'Contractors', prefix: 'contractors', perms: ['read', 'write', 'delete'] },
  { resource: 'Expenses', prefix: 'expenses', perms: ['read', 'write', 'delete'] },
  { resource: 'Reports', prefix: 'reports', perms: ['read', 'write'] },
  { resource: 'Settings', prefix: 'settings', perms: ['read', 'write'] },
  { resource: 'Users', prefix: 'users', perms: ['read', 'write', 'delete'] },
  { resource: 'Roles', prefix: 'roles', perms: ['read', 'write'] },
  { resource: 'Organizations', prefix: 'organizations', perms: ['read'] },
  { resource: 'Audits', prefix: 'audits', perms: ['read'] },
];

const ALL_PERMISSIONS = PERMISSION_GROUPS.flatMap(g => g.perms.map(p => `${g.prefix}.${p}`));

const roles = ref<RoleItem[]>([]);
const loading = ref(true);
const saving = ref(false);
const deleting = ref(false);
const searchQuery = ref('');
const currentPage = ref(1);
const perPage = ref(20);
const meta = ref<PaginationMeta>({ page: 1, per_page: 20, total: 0, total_pages: 0 });
const errorMessage = ref('');

const showModal = ref(false);
const showDeleteDialog = ref(false);
const isEditing = ref(false);
const selectedRole = ref<RoleItem | null>(null);

const form = reactive({ name: '', description: '', permissions: [] as string[] });

async function fetchRoles() {
  loading.value = true;
  errorMessage.value = '';
  try {
    const { data } = await api.get('/roles', { params: { page: currentPage.value, per_page: perPage.value } });
    roles.value = data.data || [];
    meta.value = data.meta || { page: 1, per_page: 20, total: 0, total_pages: 0 };
  } catch {
    errorMessage.value = 'Failed to load roles. Please try again.';
  } finally { loading.value = false; }
}

function openCreateModal() {
  isEditing.value = false;
  selectedRole.value = null;
  Object.assign(form, { name: '', description: '', permissions: [] });
  errorMessage.value = '';
  showModal.value = true;
}

function openEditModal(role: RoleItem) {
  isEditing.value = true;
  selectedRole.value = role;
  Object.assign(form, { name: role.name, description: role.description || '', permissions: [...role.permissions] });
  errorMessage.value = '';
  showModal.value = true;
}

function closeModal() { showModal.value = false; selectedRole.value = null; errorMessage.value = ''; }
function confirmDelete(role: RoleItem) { selectedRole.value = role; showDeleteDialog.value = true; }

async function saveRole() {
  if (!form.name.trim()) return;
  saving.value = true;
  errorMessage.value = '';
  try {
    if (isEditing.value && selectedRole.value) {
      await api.put(`/roles/${selectedRole.value.id}`, {
        name: form.name.trim(), description: form.description.trim() || null, permissions: form.permissions,
      });
    } else {
      await api.post('/roles', {
        name: form.name.trim(), description: form.description.trim() || null,
        permissions: form.permissions, is_system_role: false,
      });
    }
    closeModal();
    await fetchRoles();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error?.message || 'Failed to save role.';
  } finally { saving.value = false; }
}

async function deleteRole() {
  if (!selectedRole.value) return;
  deleting.value = true;
  try {
    await api.delete(`/roles/${selectedRole.value.id}`);
    showDeleteDialog.value = false;
    selectedRole.value = null;
    await fetchRoles();
  } catch {
    errorMessage.value = 'Failed to delete role.';
  } finally { deleting.value = false; }
}

function togglePermission(perm: string) {
  const idx = form.permissions.indexOf(perm);
  if (idx === -1) form.permissions.push(perm);
  else form.permissions.splice(idx, 1);
}

function toggleGroupPerms(group: typeof PERMISSION_GROUPS[0]) {
  const groupPerms = group.perms.map(p => `${group.prefix}.${p}`);
  const allChecked = groupPerms.every(p => form.permissions.includes(p));
  if (allChecked) {
    form.permissions = form.permissions.filter(p => !groupPerms.includes(p));
  } else {
    groupPerms.forEach(p => { if (!form.permissions.includes(p)) form.permissions.push(p); });
  }
}

function isGroupAllChecked(group: typeof PERMISSION_GROUPS[0]) {
  return group.perms.map(p => `${group.prefix}.${p}`).every(p => form.permissions.includes(p));
}

function isGroupPartial(group: typeof PERMISSION_GROUPS[0]) {
  const groupPerms = group.perms.map(p => `${group.prefix}.${p}`);
  const checked = groupPerms.filter(p => form.permissions.includes(p));
  return checked.length > 0 && checked.length < groupPerms.length;
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

const filteredRoles = computed(() => {
  if (!searchQuery.value.trim()) return roles.value;
  const q = searchQuery.value.toLowerCase();
  return roles.value.filter(r => r.name.toLowerCase().includes(q));
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

watch(currentPage, () => { if (!isSuperAdminNoOrg.value) fetchRoles(); });
onMounted(() => { if (!isSuperAdminNoOrg.value) fetchRoles(); });
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-900">ভূমিকা / Roles</h2>
        <p class="mt-1 text-sm text-slate-500">Define roles and permissions for your organization.</p>
      </div>
      <button v-if="!isSuperAdminNoOrg" @click="openCreateModal" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 cursor-pointer">
        <Plus :size="18" /> নতুন ভূমিকা / Create Role
      </button>
    </div>

    <!-- SuperAdmin No Org Notice -->
    <div v-if="isSuperAdminNoOrg" class="rounded-xl bg-amber-50 border border-amber-200 p-6 text-center">
      <Shield :size="40" class="text-amber-400 mx-auto mb-3" />
      <h3 class="text-lg font-semibold text-slate-900">No Organization Context</h3>
      <p class="mt-2 text-sm text-slate-500 max-w-md mx-auto">
        As a Super Admin, you need to select an organization first to manage roles.
        Go to <router-link to="/organizations" class="text-emerald-600 font-medium hover:underline">Organizations</router-link> to create or manage one.
      </p>
    </div>

    <!-- Error Banner -->
    <div v-if="errorMessage" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 flex items-center gap-2">
      <span class="text-sm text-red-700 flex-1">{{ errorMessage }}</span>
      <button @click="errorMessage = ''" class="text-red-500 hover:text-red-700 cursor-pointer"><X :size="16" /></button>
    </div>

    <!-- Search -->
    <div class="relative">
      <Search :size="18" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
      <input v-model="searchQuery" type="text" placeholder="Search by role name…" class="block w-full rounded-lg border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-6">
      <div class="animate-pulse space-y-4"><div v-for="i in 5" :key="i" class="h-12 bg-slate-100 rounded-lg"></div></div>
      <div class="mt-6 flex items-center justify-center gap-2 text-sm text-slate-400">
        <Loader2 :size="16" class="animate-spin" /> Loading roles…
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="roles.length === 0" class="flex flex-col items-center justify-center py-20 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <div class="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mb-4"><Shield :size="32" class="text-slate-400" /></div>
      <h3 class="text-lg font-semibold text-slate-900">No roles found</h3>
      <p class="mt-1 text-sm text-slate-500 max-w-sm text-center">Get started by creating your first role.</p>
      <button @click="openCreateModal" class="mt-4 inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 cursor-pointer">
        <Plus :size="16" /> নতুন ভূমিকা / Create Role
      </button>
    </div>

    <!-- No Search Results -->
    <div v-else-if="filteredRoles.length === 0 && searchQuery" class="flex flex-col items-center justify-center py-16 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <Search :size="32" class="text-slate-300 mb-3" />
      <p class="text-sm text-slate-500">No roles match "{{ searchQuery }}"</p>
    </div>

    <!-- Data -->
    <template v-else>
      <!-- Table (Desktop) -->
      <div class="hidden md:block rounded-xl bg-white border border-slate-200/80 shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200">
            <thead class="bg-slate-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Name</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Description</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Permissions</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">System</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="role in filteredRoles" :key="role.id" class="hover:bg-slate-50/50 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-lg bg-emerald-100 flex items-center justify-center flex-shrink-0">
                      <Shield :size="16" class="text-emerald-700" />
                    </div>
                    <span class="text-sm font-medium text-slate-900">{{ role.name }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 text-sm text-slate-500 max-w-xs truncate">{{ role.description || '—' }}</td>
                <td class="px-6 py-4">
                  <div class="flex flex-wrap gap-1 max-w-xs">
                    <span v-for="p in role.permissions.slice(0, 3)" :key="p" class="inline-block rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">{{ p }}</span>
                    <span v-if="role.permissions.length > 3" class="inline-block rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-500">+{{ role.permissions.length - 3 }}</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span v-if="role.is_system_role" class="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">
                    <Lock :size="12" /> System
                  </span>
                  <span v-else class="text-xs text-slate-400">—</span>
                </td>
                <td class="px-6 py-4">
                  <span :class="['inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium', role.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600']">
                    <span :class="['w-1.5 h-1.5 rounded-full', role.is_active ? 'bg-emerald-500' : 'bg-red-400']"></span>
                    {{ role.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right">
                  <div class="flex items-center justify-end gap-1">
                    <button @click="openEditModal(role)" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer" title="Edit"><Edit :size="16" /></button>
                    <button v-if="!role.is_system_role && authStore.isSuperAdmin" @click="confirmDelete(role)" class="rounded-lg p-2 text-slate-400 hover:bg-red-50 hover:text-red-600 transition-colors cursor-pointer" title="Delete"><Trash2 :size="16" /></button>
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
        <div v-for="role in filteredRoles" :key="role.id" class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-4 space-y-3">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center flex-shrink-0">
                <Shield :size="18" class="text-emerald-700" />
              </div>
              <div>
                <p class="text-sm font-semibold text-slate-900">{{ role.name }}</p>
                <p class="text-xs text-slate-400">{{ role.description || 'No description' }}</p>
              </div>
            </div>
            <span :class="['inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium', role.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600']">
              <span :class="['w-1.5 h-1.5 rounded-full', role.is_active ? 'bg-emerald-500' : 'bg-red-400']"></span>
              {{ role.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div class="flex flex-wrap gap-1">
            <span v-for="p in role.permissions.slice(0, 4)" :key="p" class="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">{{ p }}</span>
            <span v-if="role.permissions.length > 4" class="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-500">+{{ role.permissions.length - 4 }}</span>
            <span v-if="role.is_system_role" class="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2 py-0.5 text-[11px] font-medium text-amber-700">
              <Lock :size="10" /> System
            </span>
          </div>
          <div class="flex items-center gap-2 pt-1 border-t border-slate-100">
            <button @click="openEditModal(role)" class="flex-1 flex items-center justify-center gap-1.5 rounded-lg border border-slate-200 py-2 text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer"><Edit :size="13" /> Edit</button>
            <button v-if="!role.is_system_role && authStore.isSuperAdmin" @click="confirmDelete(role)" class="flex items-center justify-center rounded-lg border border-red-200 px-3 py-2 text-xs font-medium text-red-600 hover:bg-red-50 transition-colors cursor-pointer"><Trash2 :size="13" /></button>
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
      <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeModal"></div>
        <div class="relative w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-2xl bg-white shadow-2xl">
          <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 sticky top-0 bg-white rounded-t-2xl z-10">
            <div class="flex items-center gap-2">
              <ShieldCheck :size="20" class="text-emerald-600" />
              <h3 class="text-lg font-semibold text-slate-900">{{ isEditing ? 'Edit Role' : 'নতুন ভূমিকা / Create Role' }}</h3>
            </div>
            <button @click="closeModal" class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer"><X :size="20" /></button>
          </div>
          <form @submit.prevent="saveRole" class="p-6 space-y-4">
            <div v-if="errorMessage" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">{{ errorMessage }}</div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Role Name <span class="text-red-500">*</span></label>
              <input v-model="form.name" type="text" required placeholder="e.g. Site Manager" :class="inputCls" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Description</label>
              <textarea v-model="form.description" rows="2" placeholder="Brief description of this role…" class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 resize-none"></textarea>
            </div>
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="block text-sm font-medium text-slate-700">Permissions</label>
                <button type="button" @click="form.permissions.length === ALL_PERMISSIONS.length ? form.permissions = [] : form.permissions = [...ALL_PERMISSIONS]" class="text-xs font-medium text-emerald-600 hover:text-emerald-700 cursor-pointer">
                  {{ form.permissions.length === ALL_PERMISSIONS.length ? 'Deselect All' : 'Select All' }}
                </button>
              </div>
              <div class="space-y-2 max-h-60 overflow-y-auto pr-1">
                <div v-for="group in PERMISSION_GROUPS" :key="group.resource" class="rounded-lg border border-slate-200 p-3">
                  <button type="button" @click="toggleGroupPerms(group)" class="flex items-center gap-2 w-full text-left cursor-pointer">
                    <span :class="['flex h-4 w-4 items-center justify-center rounded border transition-colors', isGroupAllChecked(group) ? 'bg-emerald-600 border-emerald-600' : isGroupPartial(group) ? 'border-emerald-400 bg-emerald-50' : 'border-slate-300']">
                      <svg v-if="isGroupAllChecked(group)" class="h-3 w-3 text-white" viewBox="0 0 12 12" fill="none"><path d="M10 3L4.5 8.5L2 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                      <svg v-else-if="isGroupPartial(group)" class="h-3 w-3 text-emerald-600" viewBox="0 0 12 12" fill="none"><path d="M2 6h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                    </span>
                    <span class="text-sm font-medium text-slate-800">{{ group.resource }}</span>
                    <span class="text-[11px] text-slate-400 ml-auto">{{ group.perms.filter(p => form.permissions.includes(`${group.prefix}.${p}`)).length }}/{{ group.perms.length }}</span>
                  </button>
                  <div class="ml-6 mt-2 flex flex-wrap gap-x-4 gap-y-1">
                    <label v-for="p in group.perms" :key="p" class="flex items-center gap-1.5 cursor-pointer">
                      <input type="checkbox" :checked="form.permissions.includes(`${group.prefix}.${p}`)" @change="togglePermission(`${group.prefix}.${p}`)" class="h-3.5 w-3.5 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500/20 cursor-pointer" />
                      <span class="text-xs text-slate-600 capitalize">{{ p }}</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
            <div class="flex items-center justify-end gap-3 pt-2">
              <button type="button" @click="closeModal" class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
              <button type="submit" :disabled="saving" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer">
                <Loader2 v-if="saving" :size="16" class="animate-spin" />{{ isEditing ? 'Update Role' : 'Create Role' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation -->
    <Teleport to="body">
      <div v-if="showDeleteDialog" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showDeleteDialog = false"></div>
        <div class="relative w-full max-w-sm rounded-2xl bg-white shadow-2xl p-6 text-center">
          <div class="mx-auto mb-4 w-14 h-14 rounded-full bg-red-50 flex items-center justify-center"><Trash2 :size="24" class="text-red-500" /></div>
          <h3 class="text-lg font-semibold text-slate-900">Delete Role?</h3>
          <p class="mt-2 text-sm text-slate-500">Are you sure you want to delete <strong class="text-slate-700">{{ selectedRole?.name }}</strong>? Users with this role will lose its permissions.</p>
          <div class="mt-6 flex items-center gap-3">
            <button @click="showDeleteDialog = false" class="flex-1 rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
            <button @click="deleteRole" :disabled="deleting" class="flex-1 inline-flex items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60 transition-colors cursor-pointer">
              <Loader2 v-if="deleting" :size="16" class="animate-spin" />Delete
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
