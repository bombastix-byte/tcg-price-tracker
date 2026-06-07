import { Platform } from "react-native";

const API_BASE = Platform.select({
  android: "http://10.0.2.2:8000",  // Android emulator -> localhost
  default: "http://localhost:8000",  // iOS simulator, web, physical device
});

export interface MarketplaceLink {
  id: number;
  product_id: number;
  marketplace: "cardmarket" | "ebay" | "amazon";
  url: string;
  external_id: string;
}

export interface Product {
  id: number;
  name: string;
  tcg: "pokemon" | "magic";
  category: string;
  set_name: string;
  set_code: string;
  image_url: string;
  release_date: string | null;
  created_at: string;
  lowest_prices?: Record<string, number | null>;
  marketplace_links?: MarketplaceLink[];
}

export interface Price {
  id: number;
  product_id: number;
  marketplace: "cardmarket" | "ebay" | "amazon";
  price: number;
  currency: string;
  condition: string;
  seller: string;
  url: string;
  scraped_at: string;
}

export interface PriceHistoryPoint {
  date: string;
  cardmarket: number | null;
  ebay: number | null;
  amazon: number | null;
}

export interface Alert {
  id: number;
  product_id: number;
  user_device_token: string;
  target_price: number;
  direction: "below" | "above";
  is_active: boolean;
  created_at: string;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(`API Error ${res.status}: ${error}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Products
export const getProducts = (params?: {
  tcg?: string;
  category?: string;
  search?: string;
}) => {
  const query = new URLSearchParams();
  if (params?.tcg) query.set("tcg", params.tcg);
  if (params?.category) query.set("category", params.category);
  if (params?.search) query.set("search", params.search);
  const qs = query.toString();
  return request<Product[]>(`/products/${qs ? `?${qs}` : ""}`);
};

export const getProduct = (id: number) =>
  request<Product>(`/products/${id}`);

// Prices
export const getPrices = (productId: number) =>
  request<Price[]>(`/prices/products/${productId}/prices`);

export const refreshPrices = (productId: number) =>
  request<Price[]>(`/prices/products/${productId}/prices/refresh`, {
    method: "POST",
  });

export const getPriceHistory = (productId: number, days = 30) =>
  request<PriceHistoryPoint[]>(
    `/prices/products/${productId}/history?days=${days}`
  );

// Alerts
export const getAlerts = (deviceToken: string) =>
  request<Alert[]>(`/alerts/?device_token=${encodeURIComponent(deviceToken)}`);

export const createAlert = (data: {
  product_id: number;
  user_device_token: string;
  target_price: number;
  direction: "below" | "above";
}) => request<Alert>("/alerts/", { method: "POST", body: JSON.stringify(data) });

export const updateAlert = (
  id: number,
  data: Partial<{ target_price: number; direction: string; is_active: boolean }>
) =>
  request<Alert>(`/alerts/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });

export const deleteAlert = (id: number) =>
  request<void>(`/alerts/${id}`, { method: "DELETE" });

// Marketplace Links
export const createMarketplaceLink = (
  productId: number,
  data: { marketplace: string; url: string; external_id?: string }
) =>
  request<MarketplaceLink>(`/products/${productId}/links`, {
    method: "POST",
    body: JSON.stringify(data),
  });

export const deleteMarketplaceLink = (productId: number, linkId: number) =>
  request<void>(`/products/${productId}/links/${linkId}`, {
    method: "DELETE",
  });
