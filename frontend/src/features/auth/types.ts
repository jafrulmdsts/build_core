export interface TokenData {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginResponse {
  token: TokenData;
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_super_admin: boolean;
  organization_id: string | null;
  role_id: string | null;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_super_admin: boolean;
  organization_id: string | null;
  role_id: string | null;
  phone?: string;
  avatar_url?: string;
  language_preference?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  token: string;
  first_name: string;
  last_name: string;
  password: string;
  phone: string;
}

export interface InviteRequest {
  email: string;
  first_name: string;
  last_name: string;
  role_id: string;
  phone: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
  meta?: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}

export interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Array<{ field: string; message: string }>;
  };
}
