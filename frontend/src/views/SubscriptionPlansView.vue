<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/features/auth/store';
import api from '@/lib/api';
import {
  Crown, Check, Loader2, Plus, Edit, Trash2, X, AlertCircle,
  ChevronDown, ChevronUp,
} from '@lucide/vue';

const { locale } = useI18n();
const isBangla = computed(() => locale.value === 'bn');
const authStore = useAuthStore();

interface Plan {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  price_monthly: number;
  price_yearly: number;
  max_users: number | null;
  max_projects: number | null;
  max_storage_mb: number | null;
  features: string[];
  trial_days: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const plans = ref<Plan[]>([]);
const loading = ref(true);
const saving = ref(false);
const errorMessage = ref('');

// Modal state
const showModal = ref(false);
const isEditing = ref(false);
const selectedPlan = ref<Plan | null>(null);
const showDeleteDialog = ref(false);
const deleting = ref(false);

const emptyForm = () => ({
  name: '',
  slug: '',
  description: '',
  price_monthly: '0' as string | number,
  price_yearly: '0' as string | number,
  max_users: '' as string | number,
  max_projects: '' as string | number,
  max_storage_mb: '' as string | number,
  trial_days: '' as string | number,
  is_active: true,
  features_text: '',
});

const form = ref(emptyForm());
const featureInput = ref('');

async function fetchPlans() {
  loading.value = true;
  errorMessage.value = '';
  try {
    const includeInactive = authStore.isSuperAdmin;
    const { data } = await api.get('/subscriptions', {
      params: includeInactive ? { include_inactive: true } : {},
    });
    if (data.success === false) {
      errorMessage.value = data.error?.message || 'Failed to load subscription plans.';
      plans.value = [];
    } else {
      plans.value = data.data || [];
    }
  } catch (err: any) {
    console.error('Failed to fetch subscription plans:', err);
    errorMessage.value = err.response?.data?.error?.message || 'Failed to load subscription plans. Please try again.';
    plans.value = [];
  } finally {
    loading.value = false;
  }
}

function formatPrice(price: number | null | undefined) {
  if (!price || price === 0) return isBangla.value ? 'বিনামূল্য' : 'Free';
  return `৳${Number(price).toLocaleString()}`;
}

function formatStorage(mb: number | null) {
  if (!mb) return '—';
  if (mb >= 1000) return `${(mb / 1000).toFixed(0)} GB`;
  return `${mb} MB`;
}

const planAccents = [
  'border-emerald-500 ring-emerald-500',
  'border-blue-500 ring-blue-500',
  'border-purple-500 ring-purple-500',
];

function openCreateModal() {
  isEditing.value = false;
  selectedPlan.value = null;
  form.value = emptyForm();
  errorMessage.value = '';
  showModal.value = true;
}

function openEditModal(plan: Plan) {
  isEditing.value = true;
  selectedPlan.value = plan;
  form.value = {
    name: plan.name,
    slug: plan.slug,
    description: plan.description || '',
    price_monthly: plan.price_monthly || '0',
    price_yearly: plan.price_yearly || '0',
    max_users: plan.max_users ?? '',
    max_projects: plan.max_projects ?? '',
    max_storage_mb: plan.max_storage_mb ?? '',
    trial_days: plan.trial_days ?? '',
    is_active: plan.is_active,
    features_text: plan.features.join('\n'),
  };
  errorMessage.value = '';
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  selectedPlan.value = null;
  errorMessage.value = '';
}

function confirmDelete(plan: Plan) {
  selectedPlan.value = plan;
  showDeleteDialog.value = true;
}

function addFeature() {
  const f = featureInput.value.trim();
  if (f && !form.value.features_text.split('\n').map(s => s.trim()).includes(f)) {
    form.value.features_text = form.value.features_text
      ? `${form.value.features_text}\n${f}`
      : f;
    featureInput.value = '';
  }
}

function removeFeatureLine(idx: number) {
  const lines = form.value.features_text.split('\n');
  lines.splice(idx, 1);
  form.value.features_text = lines.join('\n');
}

async function savePlan() {
  if (!form.value.name.trim() || !form.value.slug.trim()) return;
  saving.value = true;
  errorMessage.value = '';

  const features = form.value.features_text
    .split('\n')
    .map(s => s.trim())
    .filter(Boolean);

  const payload: Record<string, any> = {
    name: form.value.name.trim(),
    slug: form.value.slug.trim(),
    description: form.value.description.trim() || null,
    price_monthly: Number(form.value.price_monthly) || 0,
    price_yearly: Number(form.value.price_yearly) || 0,
    max_users: form.value.max_users ? Number(form.value.max_users) : null,
    max_projects: form.value.max_projects ? Number(form.value.max_projects) : null,
    max_storage_mb: form.value.max_storage_mb ? Number(form.value.max_storage_mb) : null,
    trial_days: form.value.trial_days ? Number(form.value.trial_days) : null,
    is_active: form.value.is_active,
    features,
  };

  try {
    if (isEditing.value && selectedPlan.value) {
      const { data } = await api.put(`/subscriptions/${selectedPlan.value.id}`, payload);
      if (data.success === false) {
        errorMessage.value = data.error?.message || 'Failed to update plan.';
      }
    } else {
      const { data } = await api.post('/subscriptions', payload);
      if (data.success === false) {
        errorMessage.value = data.error?.message || 'Failed to create plan.';
      }
    }
    closeModal();
    await fetchPlans();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error?.message || 'Failed to save plan.';
  } finally {
    saving.value = false;
  }
}

async function deletePlan() {
  if (!selectedPlan.value) return;
  deleting.value = true;
  try {
    await api.delete(`/subscriptions/${selectedPlan.value.id}`);
    showDeleteDialog.value = false;
    selectedPlan.value = null;
    await fetchPlans();
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error?.message || 'Failed to delete plan.';
  } finally {
    deleting.value = false;
  }
}

function generateSlug() {
  if (!form.value.name.trim()) return;
  if (isEditing.value) return; // don't auto-generate when editing
  form.value.slug = form.value.name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim();
}

const inputCls = 'block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20';

onMounted(fetchPlans);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-slate-900">{{ isBangla ? 'সাবস্ক্রিপশন প্ল্যান' : 'Subscription Plans' }}</h2>
        <p class="mt-1 text-sm text-slate-500">{{ isBangla ? 'আপনার প্রয়োজন অনুযায়ী প্ল্যান বেছে নিন' : 'Choose the plan that fits your needs' }}</p>
      </div>
      <button v-if="authStore.isSuperAdmin" @click="openCreateModal" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 cursor-pointer">
        <Plus :size="18" /> {{ isBangla ? 'নতুন প্ল্যান' : 'New Plan' }}
      </button>
    </div>

    <!-- Error Banner -->
    <div v-if="errorMessage && !showModal" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 flex items-center gap-2">
      <AlertCircle :size="16" class="text-red-500 flex-shrink-0" />
      <span class="text-sm text-red-700 flex-1">{{ errorMessage }}</span>
      <button @click="errorMessage = ''" class="text-red-500 hover:text-red-700 cursor-pointer"><X :size="16" /></button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 :size="32" class="animate-spin text-emerald-600" />
    </div>

    <!-- Empty -->
    <div v-else-if="plans.length === 0" class="flex flex-col items-center justify-center py-20 rounded-xl bg-white border border-slate-200/80 shadow-sm">
      <Crown :size="48" class="text-slate-300 mb-4" />
      <h3 class="text-lg font-semibold text-slate-900">{{ isBangla ? 'কোন প্ল্যান নেই' : 'No Plans Available' }}</h3>
      <p class="mt-1 text-sm text-slate-500 max-w-sm text-center">{{ isBangla ? 'সাবস্ক্রিপশন প্ল্যান পাওয়া যায়নি।' : 'No subscription plans found.' }}</p>
    </div>

    <!-- Plan Cards Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <div v-for="(plan, idx) in plans" :key="plan.id"
        :class="['rounded-xl border-2 bg-white shadow-sm p-6 flex flex-col transition-shadow hover:shadow-md relative', !plan.is_active ? 'opacity-60 border-slate-200' : planAccents[idx % planAccents.length]]">
        <!-- Inactive Badge -->
        <span v-if="!plan.is_active" class="absolute top-3 right-3 inline-flex items-center rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-500">
          Inactive
        </span>
        <!-- Admin Actions -->
        <div v-if="authStore.isSuperAdmin" class="absolute top-3 right-3 flex items-center gap-1">
          <button @click="openEditModal(plan)" class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer" title="Edit"><Edit :size="14" /></button>
          <button @click="confirmDelete(plan)" class="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 transition-colors cursor-pointer" title="Delete"><Trash2 :size="14" /></button>
        </div>

        <!-- Plan Header -->
        <div class="mb-6">
          <h3 class="text-lg font-bold text-slate-900">{{ plan.name }}</h3>
          <div class="mt-3 flex items-baseline gap-1">
            <span class="text-3xl font-bold text-slate-900">{{ formatPrice(plan.price_monthly) }}</span>
            <span v-if="plan.price_monthly > 0" class="text-sm text-slate-500">/ {{ isBangla ? 'মাসিক' : 'mo' }}</span>
          </div>
          <p v-if="plan.price_yearly > 0 && plan.price_monthly > 0" class="mt-1 text-xs text-emerald-600 font-medium">
            {{ isBangla ? 'বার্ষিক' : 'Yearly' }}: ৳{{ Number(plan.price_yearly).toLocaleString() }}
          </p>
          <p v-if="plan.description" class="mt-2 text-sm text-slate-500 line-clamp-2">{{ plan.description }}</p>
        </div>

        <!-- Limits -->
        <div class="flex gap-4 mb-6">
          <div class="flex items-center gap-1.5 text-sm text-slate-600">
            <span class="font-semibold text-slate-900">{{ plan.max_users ?? '∞' }}</span>
            {{ isBangla ? 'ব্যবহারকারী' : 'Users' }}
          </div>
          <div class="flex items-center gap-1.5 text-sm text-slate-600">
            <span class="font-semibold text-slate-900">{{ plan.max_projects ?? '∞' }}</span>
            {{ isBangla ? 'প্রকল্প' : 'Projects' }}
          </div>
          <div class="flex items-center gap-1.5 text-sm text-slate-600">
            <span class="font-semibold text-slate-900">{{ formatStorage(plan.max_storage_mb) }}</span>
          </div>
        </div>

        <!-- Trial Badge -->
        <div v-if="plan.trial_days" class="mb-4">
          <span class="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">
            {{ plan.trial_days }} {{ isBangla ? 'দিনের ট্রায়াল' : 'day trial' }}
          </span>
        </div>

        <!-- Features -->
        <ul v-if="plan.features.length > 0" class="space-y-2.5 flex-1 mb-6">
          <li v-for="feature in plan.features" :key="feature" class="flex items-start gap-2 text-sm text-slate-600">
            <Check :size="16" class="text-emerald-500 flex-shrink-0 mt-0.5" />
            <span>{{ feature }}</span>
          </li>
        </ul>

        <!-- CTA -->
        <button class="w-full rounded-lg py-2.5 text-sm font-semibold transition-colors cursor-pointer"
          :class="plan.price_monthly === 0 ? 'bg-slate-100 text-slate-700 hover:bg-slate-200' : 'bg-emerald-600 text-white hover:bg-emerald-700'">
          {{ plan.price_monthly === 0 ? (isBangla ? 'বিনামূল্য প্ল্যান' : 'Free Plan') : (isBangla ? 'আপগ্রেড করুন' : 'Upgrade') }}
        </button>
      </div>
    </div>
  </div>

  <!-- Create / Edit Plan Modal -->
  <Teleport to="body">
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeModal"></div>
      <div class="relative w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-2xl bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 sticky top-0 bg-white rounded-t-2xl z-10">
          <h3 class="text-lg font-semibold text-slate-900">
            {{ isEditing ? 'Edit Plan' : (isBangla ? 'নতুন সাবস্ক্রিপশন প্ল্যান' : 'New Subscription Plan') }}
          </h3>
          <button @click="closeModal" class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer"><X :size="20" /></button>
        </div>
        <form @submit.prevent="savePlan" class="p-6 space-y-4">
          <div v-if="errorMessage" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700 flex items-center gap-2">
            <AlertCircle :size="16" class="flex-shrink-0" />{{ errorMessage }}
          </div>

          <!-- Name & Slug -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Plan Name <span class="text-red-500">*</span></label>
              <input v-model="form.name" @input="generateSlug" type="text" required placeholder="e.g. Enterprise" :class="inputCls" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Slug <span class="text-red-500">*</span></label>
              <input v-model="form.slug" type="text" required placeholder="e.g. enterprise" pattern="[a-z0-9-]+" :class="inputCls" />
            </div>
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Description</label>
            <textarea v-model="form.description" rows="2" placeholder="Brief description of this plan..." class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 resize-none"></textarea>
          </div>

          <!-- Prices -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Monthly Price (BDT)</label>
              <input v-model="form.price_monthly" type="number" min="0" step="0.01" placeholder="0" :class="inputCls" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Yearly Price (BDT)</label>
              <input v-model="form.price_yearly" type="number" min="0" step="0.01" placeholder="0" :class="inputCls" />
            </div>
          </div>

          <!-- Limits -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Max Users</label>
              <input v-model="form.max_users" type="number" min="0" placeholder="∞" :class="inputCls" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Max Projects</label>
              <input v-model="form.max_projects" type="number" min="0" placeholder="∞" :class="inputCls" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Storage (MB)</label>
              <input v-model="form.max_storage_mb" type="number" min="0" placeholder="500" :class="inputCls" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Trial Days</label>
              <input v-model="form.trial_days" type="number" min="0" placeholder="0" :class="inputCls" />
            </div>
          </div>

          <!-- Features -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Features (one per line)</label>
            <textarea v-model="form.features_text" rows="4" placeholder="Up to 10 users&#10;Up to 20 projects&#10;Priority support" class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 resize-none font-mono"></textarea>
            <p class="mt-1 text-xs text-slate-400">Enter each feature on a new line.</p>
          </div>

          <!-- Active Toggle -->
          <div>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="form.is_active" type="checkbox" class="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500 h-4 w-4" />
              <span class="text-sm text-slate-700">Plan is active</span>
            </label>
          </div>

          <!-- Actions -->
          <div class="flex items-center justify-end gap-3 pt-2">
            <button type="button" @click="closeModal" class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
            <button type="submit" :disabled="saving" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer">
              <Loader2 v-if="saving" :size="16" class="animate-spin" />{{ isEditing ? 'Update Plan' : 'Create Plan' }}
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
        <h3 class="text-lg font-semibold text-slate-900">Delete Plan?</h3>
        <p class="mt-2 text-sm text-slate-500">Are you sure you want to delete <strong class="text-slate-700">{{ selectedPlan?.name }}</strong>? This action cannot be undone.</p>
        <div class="mt-6 flex items-center gap-3">
          <button @click="showDeleteDialog = false" class="flex-1 rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer">Cancel</button>
          <button @click="deletePlan" :disabled="deleting" class="flex-1 inline-flex items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60 transition-colors cursor-pointer">
            <Loader2 v-if="deleting" :size="16" class="animate-spin" />Delete
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
