<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import api from '@/lib/api';
import { useAuthStore } from '@/features/auth/store';
import {
  Users, UserPlus, Search, Edit, Trash2, X, Mail, Phone,
  ChevronLeft, ChevronRight, Loader2, Shield, Copy, Check,
  UserRound, EyeOff, Eye, Lock, Building2,
} from '@lucide/vue';

const { t } = useI18n();
const authStore = useAuthStore();

interface Role { id: string; name: string; }
interface OrgItem { id: string; name: string; slug: string; }
interface UserItem {
  id: string; email: string; first_name: string; last_name: string;
  phone: string; avatar_url: string | null; role_id: string;
  is_active: boolean; is_super_admin: boolean; organization_id: string;
  language_preference: string; created_at: string; updated_at: string;
}
interface PaginationMeta { page: number; per_page: number; total: number; total_pages: number; }

const users = ref<UserItem[]>([]);
const roles = ref<Role[]>([]);
const organizations = ref<OrgItem[]>([]);
const loading = ref(true);
const saving = ref(false);
const searchQuery = ref('');
const currentPage = ref(1);
const perPage = ref(20);
const meta = ref<PaginationMeta>({ page: 1, per_page: 20, total: 0, total_pages: 0 });
const errorMessage = ref('');

// Modals
const showInviteModal = ref(false);
const showCreateUserModal = ref(false);
const showEditModal = ref(false);
const showDeleteDialog = ref(false);
const inviteLink = ref('');
const linkCopied = ref(false);
const deleting = ref(false);

// Selected user for edit/delete
const selectedUser = ref<UserItem | null>(null);

// Invite form
const inviteForm = reactive({ email: '', first_name: '', last_name: '', phone: '', role_id: '' });
const editForm = reactive({ first_name: '', last_name: '', phone: '', email: '', role_id: '' });

// Superadmin create user form
const createUserForm = reactive({
  organization_id: '', email: '', first_name: '', last_name: '',
  password: '', phone: '', role_id: '', is_active: true,
});

const isSuperAdminNoOrg = computed(() => authStore.isSuperAdmin && !authStore.hasOrganization);

async function fetchUsers() {
  loading.value = true;
  errorMessage.value = '';
  try {
    const { data } = await api.get('/users', { params: { page: currentPage.value, per_page: perPage.value } });
    users.value = data.data || [];
    meta.value = data.meta || { page: 1, per_page: 20, total: 0, total_pages: 0 };
  } catch {
    errorMessage.value = 'Failed to load users. Please try again.';
  } finally { loading.value = false; }
}

async function fetchRoles() {
  const orgId = authStore.user?.organization_id;
  if (!orgId) return;
  try {
    const { data } = await api.get('/roles', { params: { organization_id: orgId } });
    roles.value = data.data || [];
  } catch { /* roles dropdown is optional */ }
}

async function fetchRolesForOrg(orgId: string) {
  if (!orgId) { roles.value = []; return; }
  try {
    const { data } = await api.get('/roles', { params: { organization_id: orgId } });
    roles.value = data.data || [];
  } catch { roles.value = []; }
}

async function fetchOrganizations() {
  if (!authStore.isSuperAdmin) return;
  try {
    const { data } = await api.get('/organizations', { params: { page: 1, per_page: 100 } });
    organizations.value = (data.data || []).map((o: any) => ({ id: o.id, name: o.name, slug: o.slug }));
  } catch { /* optional */ }
}

async function inviteUser() {
  if (!inviteForm.email.trim() || !inviteForm.first_name.trim()) return;
  saving.value = true;
  errorMessage.value = '';
  try {
    const { data } = await api.post('/auth/invite', {
      email: inviteForm.email.trim(), first_name: inviteForm.first_name.trim(),
      last_name: inviteForm.last_name.trim(), phone: inviteForm.phone.trim() || undefined,
      role_id: inviteForm.role_id || undefined,
    });
    inviteLink.value = `${window.location.origin}/register/${data.data.invite_token}`;
    Object.assign(inviteForm, { email: '', first_name: '', last_name: '', phone: '', role_id: '' });
    await fetchUsers();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error?.message || 'Failed to send invitation.';
  } finally { saving.value = false; }
}

async function createSuperAdminUser() {
  if (!createUserForm.organization_id || !createUserForm.email.trim() || !createUserForm.first_name.trim() || !createUserForm.password) return;
  saving.value = true;
  errorMessage.value = '';
  try {
    await api.post('/users/create', {
      organization_id: createUserForm.organization_id,
      email: createUserForm.email.trim(),
      first_name: createUserForm.first_name.trim(),
      last_name: createUserForm.last_name.trim(),
      password: createUserForm.password,
      phone: createUserForm.phone.trim() || undefined,
      role_id: createUserForm.role_id || undefined,
      is_active: createUserForm.is_active,
    });
    closeCreateUserModal();
    await fetchUsers();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error?.message || 'Failed to create user.';
  } finally { saving.value = false; }
}

async function updateUser() {
  if (!selectedUser.value) return;
  saving.value = true;
  errorMessage.value = '';
  try {
    await api.put(`/users/${selectedUser.value.id}`, {
      first_name: editForm.first_name.trim(), last_name: editForm.last_name.trim(),
      phone: editForm.phone.trim() || null, email: editForm.email.trim(),
      role_id: editForm.role_id || null,
    });
    closeEditModal();
    await fetchUsers();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error?.message || 'Failed to update user.';
  } finally { saving.value = false; }
}

async function deleteUser() {
  if (!selectedUser.value) return;
  deleting.value = true;
  try {
    await api.delete(`/users/${selectedUser.value.id}`);
    showDeleteDialog.value = false;
    selectedUser.value = null;
    await fetchUsers();
  } catch {
    errorMessage.value = 'Failed to delete user.';
  } finally { deleting.value = false; }
}

async function toggleUserStatus(user: UserItem) {
  try {
    const endpoint = user.is_active ? 'deactivate' : 'activate';
    await api.patch(`/users/${user.id}/${endpoint}`);
    user.is_active = !user.is_active;
  } catch {
    errorMessage.value = `Failed to ${user.is_active ? 'deactivate' : 'activate'} user.`;
  }
}

function getRoleName(roleId: string | null): string {
  if (!roleId) return '—';
  return roles.value.find(r => r.id === roleId)?.name || 'Unknown';
}

function getInitials(user: UserItem): string {
  return (user.first_name?.charAt(0)?.toUpperCase() || '') + (user.last_name?.charAt(0)?.toUpperCase() || '');
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function openInviteModal() {
  Object.assign(inviteForm, { email: '', first_name: '', last_name: '', phone: '', role_id: '' });
  inviteLink.value = '';
  linkCopied.value = false;
  errorMessage.value = '';
  showInviteModal.value = true;
  fetchRoles();
}

function openCreateUserModal() {
  Object.assign(createUserForm, {
    organization_id: '', email: '', first_name: '', last_name: '',
    password: '', phone: '', role_id: '', is_active: true,
  });
  errorMessage.value = '';
  roles.value = [];
  showCreateUserModal.value = true;
}

function openEditModal(user: UserItem) {
  selectedUser.value = user;
  Object.assign(editForm, {
    first_name: user.first_name, last_name: user.last_name,
    phone: user.phone || '', email: user.email, role_id: user.role_id || '',
  });
  errorMessage.value = '';
  showEditModal.value = true;
  fetchRoles();
}

function confirmDelete(user: UserItem) { selectedUser.value = user; showDeleteDialog.value = true; }
function closeInviteModal() { showInviteModal.value = false; inviteLink.value = ''; errorMessage.value = ''; }
function closeEditModal() { showEditModal.value = false; selectedUser.value = null; errorMessage.value = ''; }
function closeCreateUserModal() { showCreateUserModal.value = false; errorMessage.value = ''; }

async function copyInviteLink() {
  try {
    await navigator.clipboard.writeText(inviteLink.value);
    linkCopied.value = true;
    setTimeout(() => { linkCopied.value = false; }, 2000);
  } catch { /* clipboard not available */ }
}

const filteredUsers = computed(() => {
  if (!searchQuery.value.trim()) return users.value;
  const q = searchQuery.value.toLowerCase();
  return users.value.filter((u) =>
    u.first_name.toLowerCase().includes(q) || u.last_name.toLowerCase().includes(q) ||
    u.email.toLowerCase().includes(q) || `${u.first_name} ${u.last_name}`.toLowerCase().includes(q),
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

// When superadmin selects an org in create-user modal, fetch roles for that org
watch(() => createUserForm.organization_id, (orgId) => {
  if (orgId) fetchRolesForOrg(orgId);
});

watch(currentPage, () => fetchUsers());
onMounted(() => {
  if (!isSuperAdminNoOrg.value) {
    fetchUsers();
    fetchRoles();
  }
  if (authStore.isSuperAdmin) fetchOrganizations();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-900">ব্যবহারকারী / Users</h2>
        <p class="mt-1 text-sm text-slate-500">Manage user accounts and invitations.</p>
      </div>
      <div class="flex items-center gap-2">
        <!-- Superadmin: Create User directly -->
        <button v-if="authStore.isSuperAdmin" @click="openCreateUserModal" class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 cursor-pointer">
          <UserPlus :size="18" /> ব্যবহারকারী তৈরি করুন / Create User
        </button>
        <!-- Tenant user: Invite User -->
        <button v-if="!isSuperAdminNoOrg" @click="openInviteModal" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 cursor-pointer">
          <UserPlus :size="18" /> আমন্ত্রণ করুন / Invite User
        </button>
      </div>
    </div>

    <!-- SuperAdmin No Org Notice -->
    <div v-if="isSuperAdminNoOrg" class="rounded-xl bg-amber-50 border border-amber-200 p-6 text-center">
      <Building2 :size="40" class="text-amber-400 mx-auto mb-3" />
      <h3 class="text-lg font-semibold text-slate-900">No Organization Selected</h3>
      <p class="mt-2 text-sm text-slate-500 max-w-md mx-auto">
        As a Super Admin, you need to select or create an organization first to manage its users.
        Go to <router-link to="/organizations" class="text-emerald-600 font-medium hover:underline">Organizations</router-link> to create one, or use "Create User" to add users directly.
      </p>
    </div>

    <!-- Error Banner -->
    <div v-if="errorMessage && !showInviteModal && !showCreateUserModal && !showEditModal" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 flex items-center gap-2">
      <span class="text-sm text-red-700 flex-1">{{ errorMessage }}</span>
      <button @click="errorMessage = ''" class="text-red-500 hover:text-red-700 cursor-pointer"><X :size="16" /></button>
    </div>

    <!-- Search -->
    <div v-if="!isSuperAdminNoOrg" class="relative">
      <Search :size="18" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
      <input v-model="searchQuery" type="text" placeholder="Search by name or email…" class="block w-full rounded-lg border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20" />
    </div>

    <!-- Loading Skeleton -->
    <div v-if="loading" class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-6">
      <div class="animate-pulse space-y-4"><div v-for="i in 5" :key="i" class="h-12 bg-slate-100 rounded-lg"></div></div>
      <div class="mt-6 flex items-center justify-center gap-2 text-sm text-slate-400">
        <Loader2 :size="16" class="animate-spin" /> Loading users…
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="users.length === 0 && !isSuperAdminNoOrg" class="flex flex-col items-center justify-center py-20 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <div class="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mb-4"><Users :size="32" class="text-slate-400" /></div>
      <h3 class="text-lg font-semibold text-slate-900">No users found</h3>
      <p class="mt-1 text-sm text-slate-500 max-w-sm text-center">Get started by inviting your first team member.</p>
      <div class="mt-4 flex items-center gap-2">
        <button v-if="authStore.isSuperAdmin" @click="openCreateUserModal" class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-blue-700 cursor-pointer">
          <UserPlus :size="16" /> Create User
        </button>
        <button @click="openInviteModal" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 cursor-pointer">
          <UserPlus :size="16" /> Invite
        </button>
      </div>
    </div>

    <!-- No Search Results -->
    <div v-else-if="filteredUsers.length === 0 && searchQuery" class="flex flex-col items-center justify-center py-16 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <Search :size="32" class="text-slate-300 mb-3" />
      <p class="text-sm text-slate-500">No users match "{{ searchQuery }}"</p>
    </div>

    <!-- Data Display -->
    <template v-else-if="users.length > 0">
      <!-- Table (Desktop) -->
      <div class="hidden md:block rounded-xl bg-white border border-slate-200/80 shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200">
            <thead class="bg-slate-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Name</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Email</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Phone</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Role</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Created</th>
                <th class="px-6 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="user in filteredUsers" :key="user.id" class="hover:bg-slate-50/50 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center gap-3">
                    <div v-if="user.avatar_url" class="w-9 h-9 rounded-full overflow-hidden flex-shrink-0">
                      <img :src="user.avatar_url" :alt="user.first_name" class="w-full h-full object-cover" />
                    </div>
                    <div v-else class="w-9 h-9 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                      <span class="text-xs font-bold text-emerald-700">{{ getInitials(user) }}</span>
                    </div>
                    <div>
                      <span class="text-sm font-medium text-slate-900">{{ user.first_name }} {{ user.last_name }}</span>
                      <div v-if="user.is_super_admin" class="flex items-center gap-1 mt-0.5"><Shield :size="11" class="text-amber-500" /><span class="text-[11px] text-amber-600 font-medium">Super Admin</span></div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 text-sm text-slate-500">{{ user.email }}</td>
                <td class="px-6 py-4 text-sm text-slate-500">{{ user.phone || '—' }}</td>
                <td class="px-6 py-4 text-sm text-slate-500">{{ getRoleName(user.role_id) }}</td>
                <td class="px-6 py-4">
                  <span :class="['inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium', user.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600']">
                    <span :class="['w-1.5 h-1.5 rounded-full', user.is_active ? 'bg-emerald-500' : 'bg-red-400']"></span>
                    {{ user.is_active ? 'Active' : 'Deactivated' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-slate-500">{{ formatDate(user.created_at) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right">
                  <div class="flex items-center justify-end gap-1">
                    <button @click="openEditModal(user)" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer" title="Edit Profile"><Edit :size="16" /></button>
                    <button @click="toggleUserStatus(user)" :class="['rounded-lg p-2 transition-colors cursor-pointer', user.is_active ? 'text-slate-400 hover:bg-slate-100 hover:text-amber-600' : 'text-slate-400 hover:bg-slate-100 hover:text-emerald-600']" :title="user.is_active ? 'Deactivate' : 'Activate'">
                      <EyeOff v-if="user.is_active" :size="16" /><Eye v-else :size="16" />
                    </button>
                    <button v-if="authStore.isSuperAdmin" @click="confirmDelete(user)" class="rounded-lg p-2 text-slate-400 hover:bg-red-50 hover:text-red-600 transition-colors cursor-pointer" title="Delete"><Trash2 :size="16" /></button>
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
        <div v-for="user in filteredUsers" :key="user.id" class="rounded-xl bg-white border border-slate-200/80 shadow-sm p-4 space-y-3">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div v-if="user.avatar_url" class="w-10 h-10 rounded-full overflow-hidden flex-shrink-0">
                <img :src="user.avatar_url" :alt="user.first_name" class="w-full h-full object-cover" />
              </div>
              <div v-else class="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                <span class="text-sm font-bold text-emerald-700">{{ getInitials(user) }}</span>
              </div>
              <div>
                <p class="text-sm font-semibold text-slate-900">{{ user.first_name }} {{ user.last_name }}</p>
                <p class="text-xs text-slate-400">{{ user.email }}</p>
              </div>
            </div>
            <span :class="['inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium', user.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600']">
              <span :class="['w-1.5 h-1.5 rounded-full', user.is_active ? 'bg-emerald-500' : 'bg-red-400']"></span>
              {{ user.is_active ? 'Active' : 'Deactivated' }}
            </span>
          </div>
          <div class="grid grid-cols-2 gap-2 text-xs text-slate-500">
            <div v-if="user.phone" class="flex items-center gap-1.5"><Phone :size="12" class="text-slate-400" />{{ user.phone }}</div>
            <div class="flex items-center gap-1.5"><Shield :size="12" class="text-slate-400" />{{ getRoleName(user.role_id) }}</div>
            <div class="flex items-center gap-1.5 col-span-2">{{ formatDate(user.created_at) }}</div>
          </div>
          <div class="flex items-center gap-2 pt-1 border-t border-slate-100">
            <button @click="openEditModal(user)" class="flex-1 flex items-center justify-center gap-1.5 rounded-lg border border-slate-200 py-2 text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer"><Edit :size="13" /> Edit</button>
            <button @click="toggleUserStatus(user)" class="flex-1 flex items-center justify-center gap-1.5 rounded-lg border py-2 text-xs font-medium transition-colors cursor-pointer" :class="user.is_active ? 'border-amber-200 text-amber-600 hover:bg-amber-50' : 'border-emerald-200 text-emerald-600 hover:bg-emerald-50'">
              <EyeOff v-if="user.is_active" :size="13" /><Eye v-else :size="13" /> {{ user.is_active ? 'Deactivate' : 'Activate' }}
            </button>
            <button v-if="authStore.isSuperAdmin" @click="confirmDelete(user)" class="flex items-center justify-center rounded-lg border border-red-200 px-3 py-2 text-xs font-medium text-red-600 hover:bg-red-50 transition-colors cursor-pointer"><Trash2 :size="13" /></button>
          </div>
        </div>
        <div v-if="meta.total_pages > 1" class="flex items-center justify-center gap-2 pt-2">
          <button @click="currentPage = Math.max(1, currentPage - 1)" :disabled="currentPage <= 1" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 disabled:opacity-40 cursor-pointer"><ChevronLeft :size="16" /></button>
          <span class="text-sm text-slate-500">Page {{ currentPage }} of {{ meta.total_pages }}</span>
          <button @click="currentPage = Math.min(meta.total_pages, currentPage + 1)" :disabled="currentPage >= meta.total_pages" class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 disabled:opacity-40 cursor-pointer"><ChevronRight :size="16" /></button>
        </div>
      </div>
    </template>

    <!-- Invite User Modal -->
    <Teleport to="body">
      <div v-if="showInviteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeInviteModal"></div>
        <div class="relative w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-2xl bg-white shadow-2xl">
          <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 sticky top-0 bg-white rounded-t-2xl z-10">
            <h3 class="text-lg font-semibold text-slate-900">আমন্ত্রণ করুন / Invite User</h3>
            <button @click="closeInviteModal" class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer"><X :size="20" /></button>
          </div>
          <!-- Invite Link Success -->
          <div v-if="inviteLink" class="p-6 space-y-4">
            <div class="flex items-center gap-3 rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-3">
              <Check :size="20" class="text-emerald-600 flex-shrink-0" />
              <span class="text-sm text-emerald-700 font-medium">Invitation sent successfully!</span>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Invite Link</label>
              <div class="flex items-center gap-2">
                <input :value="inviteLink" readonly class="flex-1 rounded-lg border border-slate-300 bg-slate-50 py-2.5 px-3 text-sm text-slate-600 font-mono" />
                <button @click="copyInviteLink" :class="['rounded-lg px-3 py-2.5 text-sm font-medium transition-colors cursor-pointer flex items-center gap-1.5', linkCopied ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600 hover:bg-slate-200']">
                  <Check v-if="linkCopied" :size="16" /><Copy v-else :size="16" />{{ linkCopied ? 'Copied' : 'Copy' }}
                </button>
              </div>
            </div>
            <div class="flex justify-end pt-2">
              <button @click="closeInviteModal" class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer">Done</button>
            </div>
          </div>
          <!-- Invite Form -->
          <form v-else @submit.prevent="inviteUser" class="p-6 space-y-4">
            <div v-if="errorMessage" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">{{ errorMessage }}</div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Email <span class="text-red-500">*</span></label>
              <div class="relative"><Mail :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="inviteForm.email" type="email" required placeholder="user@example.com" :class="inputIconCls" /></div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">First Name <span class="text-red-500">*</span></label>
                <div class="relative"><UserRound :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="inviteForm.first_name" type="text" required placeholder="John" :class="inputIconCls" /></div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Last Name</label>
                <input v-model="inviteForm.last_name" type="text" placeholder="Doe" :class="inputCls" />
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Phone</label>
                <div class="relative"><Phone :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="inviteForm.phone" type="tel" placeholder="+880 1XXX-XXXXXX" :class="inputIconCls" /></div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Role</label>
                <select v-model="inviteForm.role_id" :class="inputCls + ' cursor-pointer'">
                  <option value="">— Select Role —</option>
                  <option v-for="role in roles" :key="role.id" :value="role.id">{{ role.name }}</option>
                </select>
              </div>
            </div>
            <div class="flex items-center justify-end gap-3 pt-2">
              <button type="button" @click="closeInviteModal" class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
              <button type="submit" :disabled="saving" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer">
                <Loader2 v-if="saving" :size="16" class="animate-spin" />Send Invitation
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Create User Modal (Superadmin) -->
    <Teleport to="body">
      <div v-if="showCreateUserModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeCreateUserModal"></div>
        <div class="relative w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-2xl bg-white shadow-2xl">
          <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 sticky top-0 bg-white rounded-t-2xl z-10">
            <h3 class="text-lg font-semibold text-slate-900">ব্যবহারকারী তৈরি করুন / Create User</h3>
            <button @click="closeCreateUserModal" class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer"><X :size="20" /></button>
          </div>
          <form @submit.prevent="createSuperAdminUser" class="p-6 space-y-4">
            <div v-if="errorMessage" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">{{ errorMessage }}</div>
            <!-- Organization -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Organization <span class="text-red-500">*</span></label>
              <div class="relative">
                <Building2 :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <select v-model="createUserForm.organization_id" required :class="inputIconCls + ' cursor-pointer'">
                  <option value="">— Select Organization —</option>
                  <option v-for="org in organizations" :key="org.id" :value="org.id">{{ org.name }} ({{ org.slug }})</option>
                </select>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Email <span class="text-red-500">*</span></label>
                <div class="relative"><Mail :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="createUserForm.email" type="email" required placeholder="user@example.com" :class="inputIconCls" /></div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Password <span class="text-red-500">*</span></label>
                <div class="relative"><Lock :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="createUserForm.password" type="password" required placeholder="Min 8 characters" minlength="8" :class="inputIconCls" /></div>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">First Name <span class="text-red-500">*</span></label>
                <div class="relative"><UserRound :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="createUserForm.first_name" type="text" required placeholder="John" :class="inputIconCls" /></div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Last Name</label>
                <input v-model="createUserForm.last_name" type="text" placeholder="Doe" :class="inputCls" />
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Phone</label>
                <div class="relative"><Phone :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="createUserForm.phone" type="tel" placeholder="+880 1XXX-XXXXXX" :class="inputIconCls" /></div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Role</label>
                <select v-model="createUserForm.role_id" :class="inputCls + ' cursor-pointer'">
                  <option value="">— Select Role —</option>
                  <option v-for="role in roles" :key="role.id" :value="role.id">{{ role.name }}</option>
                </select>
              </div>
            </div>
            <div>
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="createUserForm.is_active" type="checkbox" class="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500 h-4 w-4" />
                <span class="text-sm text-slate-700">Account active immediately</span>
              </label>
            </div>
            <div class="flex items-center justify-end gap-3 pt-2">
              <button type="button" @click="closeCreateUserModal" class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
              <button type="submit" :disabled="saving" class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer">
                <Loader2 v-if="saving" :size="16" class="animate-spin" />Create User
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Edit User Modal -->
    <Teleport to="body">
      <div v-if="showEditModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeEditModal"></div>
        <div class="relative w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-2xl bg-white shadow-2xl">
          <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 sticky top-0 bg-white rounded-t-2xl z-10">
            <h3 class="text-lg font-semibold text-slate-900">Edit User</h3>
            <button @click="closeEditModal" class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer"><X :size="20" /></button>
          </div>
          <form @submit.prevent="updateUser" class="p-6 space-y-4">
            <div v-if="errorMessage" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">{{ errorMessage }}</div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Email</label>
              <div class="relative"><Mail :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="editForm.email" type="email" required :class="inputIconCls" /></div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">First Name</label>
                <input v-model="editForm.first_name" type="text" :class="inputCls" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Last Name</label>
                <input v-model="editForm.last_name" type="text" :class="inputCls" />
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Phone</label>
                <div class="relative"><Phone :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" /><input v-model="editForm.phone" type="tel" placeholder="+880 1XXX-XXXXXX" :class="inputIconCls" /></div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Role</label>
                <select v-model="editForm.role_id" :class="inputCls + ' cursor-pointer'">
                  <option value="">— No Role —</option>
                  <option v-for="role in roles" :key="role.id" :value="role.id">{{ role.name }}</option>
                </select>
              </div>
            </div>
            <div class="flex items-center justify-end gap-3 pt-2">
              <button type="button" @click="closeEditModal" class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
              <button type="submit" :disabled="saving" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer">
                <Loader2 v-if="saving" :size="16" class="animate-spin" />Update
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
          <h3 class="text-lg font-semibold text-slate-900">Delete User?</h3>
          <p class="mt-2 text-sm text-slate-500">Are you sure you want to delete <strong class="text-slate-700">{{ selectedUser?.first_name }} {{ selectedUser?.last_name }}</strong>? This action cannot be undone.</p>
          <div class="mt-6 flex items-center gap-3">
            <button @click="showDeleteDialog = false" class="flex-1 rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
            <button @click="deleteUser" :disabled="deleting" class="flex-1 inline-flex items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60 transition-colors cursor-pointer">
              <Loader2 v-if="deleting" :size="16" class="animate-spin" />Delete
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
