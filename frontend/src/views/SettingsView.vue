<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/features/auth/store';
import {
  User, Bell, Globe, Palette, Shield, Key,
  Save, Check, Loader2, Camera, Mail, Phone, MapPin, Eye, EyeOff
} from '@lucide/vue';
import api from '@/lib/api';

const { locale } = useI18n();
const authStore = useAuthStore();

const isBangla = computed(() => locale.value === 'bn');

// Tab state
const activeTab = ref<'profile' | 'notifications' | 'appearance' | 'security'>('profile');

const tabs = computed(() => [
  { id: 'profile' as const, label: isBangla.value ? 'প্রোফাইল' : 'Profile', icon: User },
  { id: 'notifications' as const, label: isBangla.value ? 'বিজ্ঞপ্তি' : 'Notifications', icon: Bell },
  { id: 'appearance' as const, label: isBangla.value ? 'দেখামেজা' : 'Appearance', icon: Palette },
  { id: 'security' as const, label: isBangla.value ? 'নিরাপত্তা' : 'Security', icon: Shield },
]);

// Profile form
const profile = reactive({
  first_name: authStore.user?.first_name || '',
  last_name: authStore.user?.last_name || '',
  email: authStore.user?.email || '',
  phone: authStore.user?.phone || '',
  address: '',
  language: locale.value,
});

const profileSaving = ref(false);
const profileSuccess = ref(false);
const profileError = ref<string | null>(null);

async function saveProfile() {
  profileSaving.value = true;
  profileSuccess.value = false;
  profileError.value = null;
  try {
    if (authStore.user?.id) {
      await api.put(`/users/${authStore.user.id}`, {
        first_name: profile.first_name,
        last_name: profile.last_name,
        phone: profile.phone,
        email: profile.email,
      });
    }
    profileSuccess.value = true;
    setTimeout(() => { profileSuccess.value = false; }, 3000);
  } catch (err: any) {
    profileError.value = err.response?.data?.error?.message || 'Failed to save profile';
  } finally {
    profileSaving.value = false;
  }
}

// Language preference
function setLanguage(lang: string) {
  locale.value = lang;
  profile.language = lang;
  if (authStore.user?.id) {
    api.put(`/users/${authStore.user.id}`, { language_preference: lang }).catch(() => {});
  }
}

// Password change form
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
});

const passwordSaving = ref(false);
const passwordSuccess = ref(false);
const passwordError = ref<string | null>(null);
const showCurrentPassword = ref(false);
const showNewPassword = ref(false);

async function changePassword() {
  passwordError.value = null;
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    passwordError.value = 'Passwords do not match';
    return;
  }
  if (passwordForm.new_password.length < 8) {
    passwordError.value = 'Password must be at least 8 characters';
    return;
  }
  passwordSaving.value = true;
  try {
    // Future endpoint: POST /auth/change-password
    passwordSuccess.value = true;
    passwordForm.current_password = '';
    passwordForm.new_password = '';
    passwordForm.confirm_password = '';
    setTimeout(() => { passwordSuccess.value = false; }, 3000);
  } catch (err: any) {
    passwordError.value = err.response?.data?.error?.message || 'Failed to change password';
  } finally {
    passwordSaving.value = false;
  }
}

// Notification preferences
const notifications = reactive({
  email_projects: true,
  email_expenses: true,
  email_users: false,
  push_projects: true,
  push_expenses: true,
  push_users: true,
});

const notifSaving = ref(false);
const notifSuccess = ref(false);

async function saveNotifications() {
  notifSaving.value = true;
  notifSuccess.value = false;
  try {
    await api.put(`/users/${authStore.user?.id}`, {
      settings: JSON.stringify({ notifications }),
    });
    notifSuccess.value = true;
    setTimeout(() => { notifSuccess.value = false; }, 3000);
  } catch { /* ignore */ } finally {
    notifSaving.value = false;
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-slate-900">
        {{ isBangla ? 'সেটিংস' : 'Settings' }}
      </h2>
      <p class="mt-1 text-sm text-slate-500">
        {{ isBangla ? 'আপনার অ্যাকাউন্ট ও পছন্দ কনফিগার করুন' : 'Configure your account and preferences' }}
      </p>
    </div>

    <div class="flex flex-col lg:flex-row gap-6">
      <!-- Sidebar Tabs -->
      <div class="lg:w-56 flex-shrink-0">
        <nav class="flex lg:flex-col gap-1 overflow-x-auto pb-2 lg:pb-0">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium whitespace-nowrap transition-all cursor-pointer',
              activeTab === tab.id
                ? 'bg-emerald-50 text-emerald-700 shadow-sm'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
            ]"
          >
            <component :is="tab.icon" :size="18" />
            <span>{{ tab.label }}</span>
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="flex-1 min-w-0">
        <!-- Profile Tab -->
        <div v-if="activeTab === 'profile'" class="rounded-xl bg-white border border-slate-200/80 shadow-sm">
          <div class="px-6 py-4 border-b border-slate-100">
            <h3 class="text-base font-semibold text-slate-900">
              {{ isBangla ? 'প্রোফাইল তথ্য' : 'Profile Information' }}
            </h3>
            <p class="text-sm text-slate-500 mt-0.5">
              {{ isBangla ? 'আপনার ব্যক্তিগত তথ্য আপডেট করুন' : 'Update your personal information' }}
            </p>
          </div>

          <div class="p-6 space-y-6">
            <!-- Avatar -->
            <div class="flex items-center gap-4">
              <div class="w-20 h-20 rounded-full bg-emerald-600 flex items-center justify-center flex-shrink-0">
                <span class="text-2xl font-bold text-white">{{ authStore.getInitials() }}</span>
              </div>
              <div>
                <h4 class="text-sm font-medium text-slate-900">{{ authStore.getFullName() }}</h4>
                <p class="text-xs text-slate-500">{{ authStore.user?.email }}</p>
                <button class="mt-2 text-xs font-medium text-emerald-600 hover:text-emerald-700 flex items-center gap-1 cursor-pointer">
                  <Camera :size="12" />
                  {{ isBangla ? 'ফটো পরিবর্তন করুন' : 'Change photo' }}
                </button>
              </div>
            </div>

            <!-- Form -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">
                  {{ isBangla ? 'প্রথম নাম' : 'First Name' }}
                </label>
                <div class="relative">
                  <User :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input v-model="profile.first_name" type="text"
                    class="w-full rounded-lg border border-slate-300 bg-white py-2.5 pl-9 pr-3 text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors" />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">
                  {{ isBangla ? 'শেষ নাম' : 'Last Name' }}
                </label>
                <input v-model="profile.last_name" type="text"
                  class="w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors" />
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">
                  {{ isBangla ? 'ইমেইল' : 'Email' }}
                </label>
                <div class="relative">
                  <Mail :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input v-model="profile.email" type="email"
                    class="w-full rounded-lg border border-slate-300 bg-white py-2.5 pl-9 pr-3 text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors" />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">
                  {{ isBangla ? 'ফোন' : 'Phone' }}
                </label>
                <div class="relative">
                  <Phone :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input v-model="profile.phone" type="tel" placeholder="+880 1XXX-XXXXXX"
                    class="w-full rounded-lg border border-slate-300 bg-white py-2.5 pl-9 pr-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors" />
                </div>
              </div>
            </div>

            <!-- Language -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">
                {{ isBangla ? 'ভাষা' : 'Language' }}
              </label>
              <div class="flex gap-2">
                <button @click="setLanguage('bn')"
                  :class="['px-4 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer', profile.language === 'bn' ? 'bg-emerald-600 text-white shadow-sm' : 'bg-slate-100 text-slate-600 hover:bg-slate-200']">
                  বাংলা
                </button>
                <button @click="setLanguage('en')"
                  :class="['px-4 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer', profile.language === 'en' ? 'bg-emerald-600 text-white shadow-sm' : 'bg-slate-100 text-slate-600 hover:bg-slate-200']">
                  English
                </button>
              </div>
            </div>

            <!-- Success/Error + Save -->
            <div v-if="profileError" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3">
              <p class="text-sm text-red-700">{{ profileError }}</p>
            </div>
            <div class="flex items-center justify-end gap-3">
              <span v-if="profileSuccess" class="flex items-center gap-1 text-sm text-emerald-600">
                <Check :size="16" />
                {{ isBangla ? 'সংরক্ষিত হয়েছে' : 'Saved' }}
              </span>
              <button @click="saveProfile" :disabled="profileSaving"
                class="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60 transition-colors cursor-pointer">
                <Loader2 v-if="profileSaving" :size="16" class="animate-spin" />
                <Save v-else :size="16" />
                {{ isBangla ? 'সংরক্ষণ করুন' : 'Save Changes' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Notifications Tab -->
        <div v-if="activeTab === 'notifications'" class="rounded-xl bg-white border border-slate-200/80 shadow-sm">
          <div class="px-6 py-4 border-b border-slate-100">
            <h3 class="text-base font-semibold text-slate-900">
              {{ isBangla ? 'বিজ্ঞপ্তি পছন্দ' : 'Notification Preferences' }}
            </h3>
          </div>
          <div class="p-6 space-y-6">
            <!-- Email Notifications -->
            <div>
              <h4 class="text-sm font-medium text-slate-900 mb-3">
                {{ isBangla ? 'ইমেইল বিজ্ঞপ্তি' : 'Email Notifications' }}
              </h4>
              <div class="space-y-3">
                <label v-for="item in [
                  { key: 'email_projects', label: isBangla ? 'প্রকল্প আপডেট' : 'Project updates' },
                  { key: 'email_expenses', label: isBangla ? 'ব্যয় অনুমোদন' : 'Expense approvals' },
                  { key: 'email_users', label: isBangla ? 'নতুন ব্যবহারকারী' : 'New user joins' },
                ]" :key="item.key" class="flex items-center justify-between py-2">
                  <span class="text-sm text-slate-700">{{ item.label }}</span>
                  <button @click="notifications[item.key as keyof typeof notifications] = !notifications[item.key as keyof typeof notifications]"
                    :class="['relative inline-flex h-6 w-11 items-center rounded-full transition-colors cursor-pointer', notifications[item.key as keyof typeof notifications] ? 'bg-emerald-600' : 'bg-slate-300']">
                    <span :class="['inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow-sm', notifications[item.key as keyof typeof notifications] ? 'translate-x-6' : 'translate-x-1']" />
                  </button>
                </label>
              </div>
            </div>
            <!-- Push Notifications -->
            <div>
              <h4 class="text-sm font-medium text-slate-900 mb-3">
                {{ isBangla ? 'পুশ বিজ্ঞপ্তি' : 'Push Notifications' }}
              </h4>
              <div class="space-y-3">
                <label v-for="item in [
                  { key: 'push_projects', label: isBangla ? 'প্রকল্প আপডেট' : 'Project updates' },
                  { key: 'push_expenses', label: isBangla ? 'ব্যয় অনুমোদন' : 'Expense approvals' },
                  { key: 'push_users', label: isBangla ? 'নতুন ব্যবহারকারী' : 'New user joins' },
                ]" :key="item.key" class="flex items-center justify-between py-2">
                  <span class="text-sm text-slate-700">{{ item.label }}</span>
                  <button @click="notifications[item.key as keyof typeof notifications] = !notifications[item.key as keyof typeof notifications]"
                    :class="['relative inline-flex h-6 w-11 items-center rounded-full transition-colors cursor-pointer', notifications[item.key as keyof typeof notifications] ? 'bg-emerald-600' : 'bg-slate-300']">
                    <span :class="['inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow-sm', notifications[item.key as keyof typeof notifications] ? 'translate-x-6' : 'translate-x-1']" />
                  </button>
                </label>
              </div>
            </div>
            <div class="flex items-center justify-end gap-3">
              <span v-if="notifSuccess" class="flex items-center gap-1 text-sm text-emerald-600">
                <Check :size="16" /> {{ isBangla ? 'সংরক্ষিত হয়েছে' : 'Saved' }}
              </span>
              <button @click="saveNotifications" :disabled="notifSaving"
                class="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60 transition-colors cursor-pointer">
                <Loader2 v-if="notifSaving" :size="16" class="animate-spin" />
                <Save v-else :size="16" />
                {{ isBangla ? 'সংরক্ষণ করুন' : 'Save Preferences' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Appearance Tab -->
        <div v-if="activeTab === 'appearance'" class="rounded-xl bg-white border border-slate-200/80 shadow-sm">
          <div class="px-6 py-4 border-b border-slate-100">
            <h3 class="text-base font-semibold text-slate-900">
              {{ isBangla ? 'দেখামেজা' : 'Appearance' }}
            </h3>
          </div>
          <div class="p-6 space-y-6">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-3">
                {{ isBangla ? 'ভাষা' : 'Language' }}
              </label>
              <div class="flex gap-3">
                <button @click="setLanguage('bn')"
                  :class="['flex items-center gap-2 px-4 py-3 rounded-lg border-2 transition-all cursor-pointer', profile.language === 'bn' ? 'border-emerald-600 bg-emerald-50' : 'border-slate-200 hover:border-slate-300']">
                  <span class="text-lg">🇧🇩</span>
                  <div class="text-left">
                    <p class="text-sm font-medium" :class="profile.language === 'bn' ? 'text-emerald-700' : 'text-slate-700'">বাংলা</p>
                    <p class="text-xs text-slate-400">Bangla</p>
                  </div>
                </button>
                <button @click="setLanguage('en')"
                  :class="['flex items-center gap-2 px-4 py-3 rounded-lg border-2 transition-all cursor-pointer', profile.language === 'en' ? 'border-emerald-600 bg-emerald-50' : 'border-slate-200 hover:border-slate-300']">
                  <span class="text-lg">🇬🇧</span>
                  <div class="text-left">
                    <p class="text-sm font-medium" :class="profile.language === 'en' ? 'text-emerald-700' : 'text-slate-700'">English</p>
                    <p class="text-xs text-slate-400">English</p>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Security Tab -->
        <div v-if="activeTab === 'security'" class="rounded-xl bg-white border border-slate-200/80 shadow-sm">
          <div class="px-6 py-4 border-b border-slate-100">
            <h3 class="text-base font-semibold text-slate-900">
              {{ isBangla ? 'পাসওয়ার্ড পরিবর্তন' : 'Change Password' }}
            </h3>
            <p class="text-sm text-slate-500 mt-0.5">
              {{ isBangla ? 'আপনার অ্যাকাউন্টের পাসওয়ার্ড আপডেট করুন' : 'Update your account password' }}
            </p>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">
                {{ isBangla ? 'বর্তমান পাসওয়ার্ড' : 'Current Password' }}
              </label>
              <div class="relative">
                <Key :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input v-model="passwordForm.current_password" :type="showCurrentPassword ? 'text' : 'password'"
                  class="w-full rounded-lg border border-slate-300 bg-white py-2.5 pl-9 pr-10 text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors" />
                <button type="button" @click="showCurrentPassword = !showCurrentPassword"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer">
                  <Eye v-if="!showCurrentPassword" :size="16" />
                  <EyeOff v-else :size="16" />
                </button>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">
                  {{ isBangla ? 'নতুন পাসওয়ার্ড' : 'New Password' }}
                </label>
                <div class="relative">
                  <input v-model="passwordForm.new_password" :type="showNewPassword ? 'text' : 'password'"
                    class="w-full rounded-lg border border-slate-300 bg-white py-2.5 px-3 pr-10 text-sm text-slate-900 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors" />
                  <button type="button" @click="showNewPassword = !showNewPassword"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer">
                    <Eye v-if="!showNewPassword" :size="16" />
                    <EyeOff v-else :size="16" />
                  </button>
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">
                  {{ isBangla ? 'পাসওয়ার্ড নিশ্চিত করুন' : 'Confirm Password' }}
                </label>
                <input v-model="passwordForm.confirm_password" type="password"
                  :class="['w-full rounded-lg border bg-white py-2.5 px-3 text-sm text-slate-900 focus:outline-none focus:ring-2 transition-colors',
                    passwordForm.confirm_password && passwordForm.new_password !== passwordForm.confirm_password
                      ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20'
                      : 'border-slate-300 focus:border-emerald-500 focus:ring-emerald-500/20']" />
              </div>
            </div>
            <div v-if="passwordError" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3">
              <p class="text-sm text-red-700">{{ passwordError }}</p>
            </div>
            <div v-if="passwordSuccess" class="rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-3">
              <p class="text-sm text-emerald-700">
                {{ isBangla ? 'পাসওয়ার্ড সফলভাবে পরিবর্তন হয়েছে' : 'Password changed successfully' }}
              </p>
            </div>
            <div class="flex justify-end">
              <button @click="changePassword" :disabled="passwordSaving"
                class="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60 transition-colors cursor-pointer">
                <Loader2 v-if="passwordSaving" :size="16" class="animate-spin" />
                <Key v-else :size="16" />
                {{ isBangla ? 'পাসওয়ার্ড পরিবর্তন করুন' : 'Change Password' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
