<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { HardHat, Globe, Building2, ArrowRight } from '@lucide/vue';
import { useI18n } from 'vue-i18n';
import api from '@/lib/api';

const router = useRouter();
const { locale } = useI18n();

const isBangla = computed(() => locale.value === 'bn');

function toggleLanguage() {
  locale.value = isBangla.value ? 'en' : 'bn';
}

const form = reactive({
  name: '',
  slug: '',
  type: '',
  contact_email: '',
  phone: '',
  address: '',
});

function generateSlug(name: string) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function onNameChange() {
  if (!form.slug || form.slug === generateSlug(form.name.slice(0, -1))) {
    form.slug = generateSlug(form.name);
  }
}

const orgTypes = [
  { value: 'construction', label: 'Construction Company' },
  { value: 'real_estate', label: 'Real Estate Developer' },
  { value: 'architecture', label: 'Architecture Firm' },
  { value: 'engineering', label: 'Engineering Consultancy' },
  { value: 'contractor', label: 'General Contractor' },
  { value: 'other', label: 'Other' },
];

const loading = ref(false);
const error = ref<string | null>(null);

async function handleSubmit() {
  error.value = null;

  if (!form.name || !form.slug || !form.type || !form.contact_email) {
    error.value = 'Please fill in all required fields.';
    return;
  }

  loading.value = true;

  try {
    await api.post('/organizations', {
      name: form.name,
      slug: form.slug,
      email: form.contact_email,
      phone: form.phone,
      address: form.address,
    });

    router.push('/dashboard');
  } catch (err: any) {
    const errorMsg = err.response?.data?.error?.message || 'Failed to create organization. Please try again.';
    error.value = errorMsg;
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="flex min-h-screen bg-slate-50">
    <!-- Left Branding Panel -->
    <div
      class="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 items-center justify-center"
    >
      <div class="absolute inset-0 opacity-10">
        <svg class="w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="grid-setup" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" stroke-width="0.5" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid-setup)" />
        </svg>
      </div>

      <div class="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-emerald-500/10 blur-3xl"></div>
      <div class="absolute -bottom-24 -right-24 w-96 h-96 rounded-full bg-emerald-600/10 blur-3xl"></div>

      <div class="relative z-10 text-center px-12">
        <div class="mx-auto mb-8 w-20 h-20 rounded-2xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center backdrop-blur-sm">
          <Building2 :size="40" class="text-emerald-400" />
        </div>
        <h1 class="text-5xl font-bold text-white tracking-tight mb-4">BuildCore</h1>
        <p class="text-lg text-slate-300 font-light tracking-wide">
          Set up your organization to get started
        </p>

        <!-- Steps indicator -->
        <div class="mt-12 flex items-center justify-center gap-3">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center text-sm font-bold text-white">1</div>
            <span class="text-sm text-emerald-400 font-medium">Register</span>
          </div>
          <div class="w-8 h-px bg-slate-600"></div>
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center text-sm font-bold text-white animate-pulse">2</div>
            <span class="text-sm text-white font-medium">Setup Organization</span>
          </div>
          <div class="w-8 h-px bg-slate-600"></div>
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-sm font-bold text-slate-400">3</div>
            <span class="text-sm text-slate-500 font-medium">Start Building</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Setup Panel -->
    <div class="flex-1 flex flex-col min-h-screen bg-white">
      <!-- Top Bar -->
      <div class="flex items-center justify-between px-6 py-4 sm:px-10 sm:py-6">
        <div class="flex items-center gap-2 lg:hidden">
          <div class="w-9 h-9 rounded-lg bg-emerald-600 flex items-center justify-center">
            <HardHat :size="20" class="text-white" />
          </div>
          <span class="text-xl font-bold text-slate-900">BuildCore</span>
        </div>

        <button
          type="button"
          @click="toggleLanguage"
          class="ml-auto inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition-all hover:bg-slate-50 hover:border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-1 cursor-pointer"
        >
          <Globe :size="16" class="text-slate-500" />
          {{ isBangla ? 'EN' : 'BN' }}
        </button>
      </div>

      <!-- Form Area -->
      <div class="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div class="w-full max-w-lg">
          <!-- Header -->
          <div class="mb-8">
            <h2 class="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Set up your organization
            </h2>
            <p class="mt-2 text-sm text-slate-500">
              Create your organization to start managing projects, teams, and expenses.
            </p>
          </div>

          <!-- Setup Card -->
          <div class="rounded-xl bg-white border border-slate-200/80 shadow-lg shadow-slate-200/50 p-6 sm:p-8">
            <form @submit.prevent="handleSubmit" class="space-y-5">
              <!-- Organization Name -->
              <div>
                <label for="org_name" class="block text-sm font-medium text-slate-700 mb-1.5">
                  Organization Name <span class="text-red-500">*</span>
                </label>
                <input
                  id="org_name"
                  v-model="form.name"
                  @input="onNameChange"
                  type="text"
                  required
                  placeholder="e.g., ABC Construction Ltd."
                  class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors"
                />
              </div>

              <!-- Slug -->
              <div>
                <label for="org_slug" class="block text-sm font-medium text-slate-700 mb-1.5">
                  Slug <span class="text-red-500">*</span>
                </label>
                <input
                  id="org_slug"
                  v-model="form.slug"
                  type="text"
                  required
                  placeholder="e.g., abc-construction"
                  pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
                  class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors font-mono"
                />
                <p class="mt-1 text-xs text-slate-400">Auto-generated from name. Use lowercase letters, numbers, and hyphens only.</p>
              </div>

              <!-- Organization Type -->
              <div>
                <label for="org_type" class="block text-sm font-medium text-slate-700 mb-1.5">
                  Organization Type <span class="text-red-500">*</span>
                </label>
                <select
                  id="org_type"
                  v-model="form.type"
                  required
                  class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors cursor-pointer"
                >
                  <option value="" disabled>Select organization type</option>
                  <option v-for="orgType in orgTypes" :key="orgType.value" :value="orgType.value">
                    {{ orgType.label }}
                  </option>
                </select>
              </div>

              <!-- Contact Email -->
              <div>
                <label for="contact_email" class="block text-sm font-medium text-slate-700 mb-1.5">
                  Contact Email <span class="text-red-500">*</span>
                </label>
                <input
                  id="contact_email"
                  v-model="form.contact_email"
                  type="email"
                  required
                  placeholder="org@example.com"
                  class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors"
                />
              </div>

              <!-- Phone -->
              <div>
                <label for="org_phone" class="block text-sm font-medium text-slate-700 mb-1.5">
                  Phone Number
                </label>
                <input
                  id="org_phone"
                  v-model="form.phone"
                  type="tel"
                  placeholder="+880 1XXX-XXXXXX"
                  class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors"
                />
              </div>

              <!-- Address -->
              <div>
                <label for="org_address" class="block text-sm font-medium text-slate-700 mb-1.5">
                  Address
                </label>
                <textarea
                  id="org_address"
                  v-model="form.address"
                  rows="3"
                  placeholder="Enter organization address"
                  class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors resize-none"
                ></textarea>
              </div>

              <!-- Error Message -->
              <div v-if="error" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3">
                <div class="flex items-center gap-2">
                  <svg class="h-4 w-4 text-red-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                  </svg>
                  <p class="text-sm text-red-700">{{ error }}</p>
                </div>
              </div>

              <!-- Submit Button -->
              <button
                type="submit"
                :disabled="loading"
                class="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60 cursor-pointer"
              >
                <svg
                  v-if="loading"
                  class="h-4 w-4 animate-spin"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <span v-if="loading">Creating organization...</span>
                <span v-else class="flex items-center gap-2">
                  Create Organization
                  <ArrowRight :size="16" />
                </span>
              </button>
            </form>
          </div>

          <!-- Footer -->
          <p class="mt-6 text-center text-xs text-slate-400">
            &copy; {{ new Date().getFullYear() }} BuildCore. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
