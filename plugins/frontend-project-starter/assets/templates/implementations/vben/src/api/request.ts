export interface RequestOptions extends RequestInit {
  params?: Record<string, boolean | number | string | undefined>;
  timeout?: number;
}

const buildUrl = (url: string, params?: RequestOptions['params']) => {
  if (!params) return url;
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) query.set(key, String(value));
  });
  const queryString = query.toString();
  return queryString ? `${url}?${queryString}` : url;
};

const normalizeFormDataHeaders = (headers?: HeadersInit) => {
  if (!headers) return undefined;
  const normalized = new Headers(headers);
  normalized.delete('content-type');
  return normalized;
};

const request = async <T>(url: string, options: RequestOptions = {}) => {
  const { params, timeout, ...fetchOptions } = options;
  const controller = new AbortController();
  const timer = timeout
    ? window.setTimeout(() => controller.abort(), timeout)
    : undefined;

  try {
    const response = await fetch(buildUrl(url, params), {
      ...fetchOptions,
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }

    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      return (await response.json()) as T;
    }

    return (await response.text()) as T;
  } finally {
    if (timer) window.clearTimeout(timer);
  }
};

export const requestClient = {
  get<T>(url: string, options?: RequestOptions) {
    return request<T>(url, { ...options, method: 'GET' });
  },
  post<T>(url: string, data?: unknown, options?: RequestOptions) {
    const isFormData = data instanceof FormData;
    return request<T>(url, {
      ...options,
      method: 'POST',
      body: isFormData ? data : JSON.stringify(data ?? {}),
      headers: isFormData
        ? normalizeFormDataHeaders(options?.headers)
        : { 'Content-Type': 'application/json', ...options?.headers },
    });
  },
};
