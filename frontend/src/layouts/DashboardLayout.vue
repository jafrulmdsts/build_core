<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/features/auth/store';
import {
  LayoutDashboard,
  Building2,
  Users,
  Shield,
  HardHat,
  UserCheck,
  Wrench,
  Receipt,
  Settings,
  Menu,
  X,
  Bell,
  Globe,
  LogOut,
  ChevronDown,
} from '@lucide/vue';

const route = useRoute();
const router = useRouter();
const { locale } = useI18n();
const authStore = useAuthStore();

const sidebarOpen = ref(false);
const userMenuOpen = ref(false);
const notificationOpen = ref(false);

const isBangla = computed(() => locale.value === 'bn');

function toggleLanguage() {
  locale.value = isBangla.value ? 'en' : 'bn';
}

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value;
}

function closeSidebar() {
  sidebarOpen.value = false;
}

function closeUserMenu() {
  userMenuOpen.value = false;
}

function toggleUserMenu() {
  userMenuOpen.value = !userMenuOpen.value;
}

function handleLogout() {
  userMenuOpen.value = false;
  authStore.logout();
}

// Close sidebar on route change (mobile)
watch(() => route.path, () => {
  closeSidebar();
  userMenuOpen.value = false;
});

interface MenuItem {
  name: string;
  path: string;
  icon: any;
  superAdminOnly?: boolean;
}

const menuItems = computed<MenuItem[]>(() => {
  const items: MenuItem[] = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Users', path: '/users', icon: Users },
    { name: 'Roles', path: '/roles', icon: Shield },
    { name: 'Projects', path: '/projects', icon: HardHat },
    { name: 'Employees', path: '/employees', icon: UserCheck },
    { name: 'Contractors', path: '/contractors', icon: Wrench },
    { name: 'Expenses', path: '/expenses', icon: Receipt },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  if (authStore.isSuperAdmin) {
    items.splice(1, 0, {
      name: 'Organizations',
      path: '/organizations',
      icon: Building2,
      superAdminOnly: true,
    });
  }

  return items;
});

const currentPageTitle = computed(() => {
  const item = menuItems.value.find((item) => item.path === route.path);
  return item?.name || 'Dashboard';
});

function isActive(path: string): boolean {
  return route.path === path;
}
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-gray-50">
    <!-- Mobile sidebar overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 z-40 bg-black/50 transition-opacity lg:hidden"
      @click="closeSidebar"
    ></div>

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 lg:z-auto',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full',
      ]"
    >
      <div class="flex h-full flex-col">
        <!-- Logo -->
        <div class="flex h-16 items-center justify-between px-6 border-b border-slate-800">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-lg bg-emerald-600 flex items-center justify-center">
              <HardHat :size="20" class="text-white" />
            </div>
            <span class="text-xl font-bold text-white tracking-tight">BuildCore</span>
          </div>
          <button
            @click="closeSidebar"
            class="lg:hidden text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            <X :size="20" />
          </button>
        </div>

        <!-- Navigation Menu -->
        <nav class="flex-1 overflow-y-auto px-3 py-4">
          <ul class="space-y-1">
            <li v-for="item in menuItems" :key="item.path">
              <router-link
                :to="item.path"
                :class="[
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150',
                  isActive(item.path)
                    ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/25'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white',
                ]"
              >
                <component :is="item.icon" :size="18" />
                <span>{{ item.name }}</span>
              </router-link>
            </li>
          </ul>
        </nav>

        <!-- User Profile Section (Bottom of Sidebar) -->
        <div class="border-t border-slate-800 p-4">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-full bg-emerald-600 flex items-center justify-center flex-shrink-0">
              <span class="text-sm font-semibold text-white">
                {{ authStore.getInitials() }}
              </span>
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium text-white truncate">
                {{ authStore.getFullName() }}
              </p>
              <p class="text-xs text-slate-400 truncate">
                {{ authStore.user?.email }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="flex flex-1 flex-col overflow-hidden">
      <!-- Top Header Bar -->
      <header class="flex h-16 items-center justify-between bg-white shadow-sm px-4 sm:px-6 flex-shrink-0 z-30">
        <!-- Left: Hamburger + Page Title -->
        <div class="flex items-center gap-4">
          <!-- Hamburger (mobile only) -->
          <button
            @click="toggleSidebar"
            class="lg:hidden inline-flex items-center justify-center rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors cursor-pointer"
          >
            <Menu :size="22" />
          </button>
          <h1 class="text-lg font-semibold text-slate-900">
            {{ currentPageTitle }}
          </h1>
        </div>

        <!-- Right: Actions -->
        <div class="flex items-center gap-2 sm:gap-3">
          <!-- Language Toggle -->
          <button
            @click="toggleLanguage"
            class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 shadow-sm transition-all hover:bg-slate-50 hover:border-slate-300 cursor-pointer"
          >
            <Globe :size="14" class="text-slate-400" />
            <span>{{ isBangla ? 'EN' : 'BN' }}</span>
          </button>

          <!-- Notifications -->
          <button
            @click="notificationOpen = !notificationOpen"
            class="relative inline-flex items-center justify-center rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors cursor-pointer"
          >
            <Bell :size="20" />
            <!-- Notification badge -->
            <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          <!-- User Menu -->
          <div class="relative">
            <button
              @click="toggleUserMenu"
              class="flex items-center gap-2 rounded-lg p-1.5 hover:bg-slate-100 transition-colors cursor-pointer"
            >
              <div class="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center">
                <span class="text-xs font-semibold text-white">
                  {{ authStore.getInitials() }}
                </span>
              </div>
              <span class="hidden sm:block text-sm font-medium text-slate-700 max-w-[120px] truncate">
                {{ authStore.getFullName() }}
              </span>
              <ChevronDown :size="16" class="hidden sm:block text-slate-400" />
            </button>

            <!-- User Dropdown Menu -->
            <div
              v-if="userMenuOpen"
              class="absolute right-0 mt-2 w-56 rounded-xl bg-white border border-slate-200 shadow-lg py-1 z-50"
            >
              <!-- User Info -->
              <div class="px-4 py-3 border-b border-slate-100">
                <p class="text-sm font-medium text-slate-900 truncate">
                  {{ authStore.getFullName() }}
                </p>
                <p class="text-xs text-slate-500 truncate">
                  {{ authStore.user?.email }}
                </p>
              </div>

              <!-- Settings Link -->
              <router-link
                to="/settings"
                @click="closeUserMenu"
                class="flex items-center gap-2.5 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
              >
                <Settings :size="16" class="text-slate-400" />
                <span>Settings</span>
              </router-link>

              <!-- Logout -->
              <button
                @click="handleLogout"
                class="flex w-full items-center gap-2.5 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors cursor-pointer"
              >
                <LogOut :size="16" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-y-auto bg-gray-50 p-4 sm:p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>
