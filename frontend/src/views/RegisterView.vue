<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/features/auth/store';
import { authApi } from '@/features/auth/api';
import { HardHat, Eye, EyeOff, Globe } from '@lucide/vue';
import { useI18n } from 'vue-i18n';

const route = useRoute();
const router = useRouter();
const { locale } = useI18n();
const authStore = useAuthStore();

const token = computed(() => route.params.token as string);

const form = reactive({
  first_name: '',
  last_name: '',
  phone: '',
  password: '',
  confirm_password: '',
});

const showPassword = ref(false);
const showConfirmPassword = ref(false);
const loading = ref(false);
const error = ref<string | null>(null);
const success = ref(false);

const isBangla = computed(() => locale.value === 'bn');

function toggleLanguage() {
  locale.value = isBangla.value ? 'en' : 'bn';
}

function passwordsMatch(): boolean {
  if (!form.confirm_password) return true;
  return form.password === form.confirm_password;
}

async function handleRegister() {
  error.value = null;

  if (!form.first_name || !form.last_name || !form.password || !form.confirm_password) {
    error.value = 'Please fill in all required fields.';
    return;
  }

  if (form.password !== form.confirm_password) {
    error.value = 'Passwords do not match.';
    return;
  }

  if (form.password.length < 8) {
    error.value = 'Password must be at least 8 characters long.';
    return;
  }

  loading.value = true;

  try {
    const { data } = await authApi.register({
      token: token.value,
      first_name: form.first_name,
      last_name: form.last_name,
      password: form.password,
      phone: form.phone,
    });

    authStore.setAuth(data.data);
    success.value = true;

    setTimeout(() => {
      router.push('/dashboard');
    }, 1000);
  } catch (err: any) {
    const errorMsg = err.response?.data?.error?.message || 'Registration failed. Please try again.';
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
            <pattern id="grid-reg" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" stroke-width="0.5" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid-reg)" />
        </svg>
      </div>

      <div class="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-emerald-500/10 blur-3xl"></div>
      <div class="absolute -bottom-24 -right-24 w-96 h-96 rounded-full bg-emerald-600/10 blur-3xl"></div>

      <div class="relative z-10 text-center px-12">
        <div class="mx-auto mb-8 w-20 h-20 rounded-2xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center backdrop-blur-sm">
          <HardHat :size="40" class="text-emerald-400" />
        </div>
        <h1 class="text-5xl font-bold text-white tracking-tight mb-4">BuildCore</h1>
        <p class="text-lg text-slate-300 font-light tracking-wide">
          Complete your registration to get started
        </p>
      </div>
    </div>

    <!-- Right Registration Panel -->
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
        <div class="w-full max-w-md">
          <!-- Header -->
          <div class="mb-8">
            <h2 class="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Create your account
            </h2>
            <p class="mt-2 text-sm text-slate-500">
              You've been invited to join BuildCore. Complete your registration below.
            </p>
          </div>

          <!-- Success State -->
          <div v-if="success" class="rounded-xl bg-emerald-50 border border-emerald-200 p-8 text-center">
            <div class="mx-auto w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center mb-4">
              <svg class="w-6 h-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-emerald-900">Registration Complete!</h3>
            <p class="mt-1 text-sm text-emerald-700">Redirecting to dashboard...</p>
          </div>

          <!-- Registration Card -->
          <div v-else class="rounded-xl bg-white border border-slate-200/80 shadow-lg shadow-slate-200/50 p-8">
            <form @submit.prevent="handleRegister" class="space-y-5">
              <!-- Name Fields -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label for="first_name" class="block text-sm font-medium text-slate-700 mb-1.5">
                    First Name <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="first_name"
                    v-model="form.first_name"
                    type="text"
                    required
                    placeholder="Enter first name"
                    class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors"
                  />
                </div>
                <div>
                  <label for="last_name" class="block text-sm font-medium text-slate-700 mb-1.5">
                    Last Name <span class="text-red-500">*</span>
                  </label>
                  <input
                    id="last_name"
                    v-model="form.last_name"
                    type="text"
                    required
                    placeholder="Enter last name"
                    class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors"
                  />
                </div>
              </div>

              <!-- Phone -->
              <div>
                <label for="phone" class="block text-sm font-medium text-slate-700 mb-1.5">
                  Phone Number
                </label>
                <input
                  id="phone"
                  v-model="form.phone"
                  type="tel"
                  placeholder="Enter phone number"
                  class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors"
                />
              </div>

              <!-- Password -->
              <div>
                <label for="password" class="block text-sm font-medium text-slate-700 mb-1.5">
                  Password <span class="text-red-500">*</span>
                </label>
                <div class="relative">
                  <input
                    id="password"
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    minlength="8"
                    placeholder="Create a password"
                    class="block w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 pr-10 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors"
                  />
                  <button
                    type="button"
                    @click="showPassword = !showPassword"
                    class="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
                  >
                    <Eye v-if="!showPassword" :size="18" />
                    <EyeOff v-else :size="18" />
                  </button>
                </div>
                <p class="mt-1 text-xs text-slate-400">Must be at least 8 characters</p>
              </div>

              <!-- Confirm Password -->
              <div>
                <label for="confirm_password" class="block text-sm font-medium text-slate-700 mb-1.5">
                  Confirm Password <span class="text-red-500">*</span>
                </label>
                <div class="relative">
                  <input
                    id="confirm_password"
                    v-model="form.confirm_password"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    required
                    placeholder="Confirm your password"
                    :class="[
                      'block w-full rounded-lg border bg-white py-2.5 px-3 pr-10 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 transition-colors',
                      form.confirm_password && !passwordsMatch()
                        ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20'
                        : 'border-slate-300 focus:border-emerald-500 focus:ring-emerald-500/20',
                    ]"
                  />
                  <button
                    type="button"
                    @click="showConfirmPassword = !showConfirmPassword"
                    class="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
                  >
                    <Eye v-if="!showConfirmPassword" :size="18" />
                    <EyeOff v-else :size="18" />
                  </button>
                </div>
                <p v-if="form.confirm_password && !passwordsMatch()" class="mt-1 text-xs text-red-500">
                  Passwords do not match
                </p>
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
                <span v-if="loading">Creating account...</span>
                <span v-else>Create Account</span>
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
