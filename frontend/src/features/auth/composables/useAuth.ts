import { useAuthStore } from '../store';
import { storeToRefs } from 'pinia';

export function useAuth() {
  const store = useAuthStore();
  const { isAuthenticated, isSuperAdmin, hasOrganization, user, loading, error } = storeToRefs(store);
  return {
    ...store,
    isAuthenticated,
    isSuperAdmin,
    hasOrganization,
    user,
    loading,
    error,
  };
}
