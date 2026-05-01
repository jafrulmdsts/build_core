import api from '@/lib/api';
import type { ApiResponse, LoginResponse, InviteRequest } from './types';

export const authApi = {
  login: (email: string, password: string) =>
    api.post<ApiResponse<LoginResponse>>('/auth/login', { email, password }),

  register: (data: { token: string; first_name: string; last_name: string; password: string; phone: string }) =>
    api.post<ApiResponse<LoginResponse>>('/auth/register', data),

  refresh: (refreshToken: string) =>
    api.post<ApiResponse<{ access_token: string; refresh_token: string; token_type: string; expires_in: number }>>('/auth/refresh', { refresh_token: refreshToken }),

  logout: () =>
    api.post<ApiResponse<null>>('/auth/logout'),

  invite: (data: InviteRequest) =>
    api.post<ApiResponse<{ id: string; email: string; invite_token: string }>>('/auth/invite', data),

  me: () =>
    api.get<ApiResponse<any>>('/auth/me'),
};
