import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { authApi } from './api';
import type { User, LoginResponse } from './types';

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const accessToken = ref<string | null>(null);
  const refreshToken = ref<string | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => !!accessToken.value && !!user.value);
  const isSuperAdmin = computed(() => user.value?.is_super_admin ?? false);
  const hasOrganization = computed(() => !!user.value?.organization_id);

  // Initialize from localStorage
  function init() {
    const storedToken = localStorage.getItem('access_token');
    const storedRefresh = localStorage.getItem('refresh_token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      accessToken.value = storedToken;
      refreshToken.value = storedRefresh;
      try {
        user.value = JSON.parse(storedUser);
      } catch {
        clearAuth();
      }
    }
  }

  async function login(email: string, password: string): Promise<boolean> {
    loading.value = true;
    error.value = null;
    try {
      const { data } = await authApi.login(email, password);
      const responseData = data.data;
      setAuth(responseData);
      return true;
    } catch (err: any) {
      const errorMsg = err.response?.data?.error?.message || 'লগইন ব্যর্থ হয়েছে';
      error.value = errorMsg;
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function logout(): Promise<void> {
    try {
      if (accessToken.value) {
        await authApi.logout();
      }
    } catch {
      // Ignore logout API errors
    } finally {
      clearAuth();
      const router = useRouter();
      router.push('/login');
    }
  }

  function setAuth(data: LoginResponse) {
    user.value = {
      id: data.user_id,
      email: data.email,
      first_name: data.first_name,
      last_name: data.last_name,
      is_super_admin: data.is_super_admin,
      organization_id: data.organization_id,
      role_id: data.role_id,
    };
    accessToken.value = data.token.access_token;
    refreshToken.value = data.token.refresh_token;

    localStorage.setItem('access_token', data.token.access_token);
    localStorage.setItem('refresh_token', data.token.refresh_token);
    localStorage.setItem('user', JSON.stringify(user.value));
  }

  function clearAuth() {
    user.value = null;
    accessToken.value = null;
    refreshToken.value = null;
    error.value = null;

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  function getFullName(): string {
    if (!user.value) return '';
    return `${user.value.first_name} ${user.value.last_name || ''}`.trim();
  }

  function getInitials(): string {
    if (!user.value) return '';
    const first = user.value.first_name?.charAt(0)?.toUpperCase() || '';
    const last = user.value.last_name?.charAt(0)?.toUpperCase() || '';
    return first + last;
  }

  init();

  return {
    user,
    accessToken,
    refreshToken,
    loading,
    error,
    isAuthenticated,
    isSuperAdmin,
    hasOrganization,
    login,
    logout,
    setAuth,
    clearAuth,
    getFullName,
    getInitials,
    init,
  };
});
