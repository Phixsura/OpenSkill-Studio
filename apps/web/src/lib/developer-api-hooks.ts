/**
 * Developer Platform React Query hooks
 * Provides typed data fetching for all developer platform endpoints
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiWithAuth } from "@/lib/api";
import type {
  DeveloperAccount, App, AppVersion, AppInstallation,
  ApiKey, ApiKeyCreated, EventSubscription, AutomationRule,
  AppSummary, CreateDeveloperAccountRequest, CreateAppRequest,
  CreateAppVersionRequest, DataResponse, ListResponse,
} from "./developer-api-types";

// ── Developer Account ───────────────────────────────

export function useDeveloperAccount() {
  return useQuery({
    queryKey: ["developer", "account"],
    queryFn: async () => {
      const res = await apiWithAuth.get<DataResponse<DeveloperAccount>>("/api/v1/developer/accounts/me");
      return res.data.data;
    },
  });
}

export function useCreateDeveloperAccount() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: CreateDeveloperAccountRequest) => {
      const res = await apiWithAuth.post<DataResponse<DeveloperAccount>>("/api/v1/developer/accounts", data);
      return res.data.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["developer"] }),
  });
}

// ── Apps ─────────────────────────────────────────────

export function useDeveloperApps() {
  return useQuery({
    queryKey: ["developer", "apps"],
    queryFn: async () => {
      const res = await apiWithAuth.get<ListResponse<App>>("/api/v1/developer/apps");
      return res.data;
    },
  });
}

export function useDeveloperApp(appId: string) {
  return useQuery({
    queryKey: ["developer", "apps", appId],
    queryFn: async () => {
      const res = await apiWithAuth.get<DataResponse<App>>(`/api/v1/developer/apps/${appId}`);
      return res.data.data;
    },
    enabled: !!appId,
  });
}

export function useCreateApp() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: CreateAppRequest) => {
      const res = await apiWithAuth.post<DataResponse<App>>("/api/v1/developer/apps", data);
      return res.data.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["developer", "apps"] }),
  });
}

// ── App Versions ────────────────────────────────────

export function useAppVersions(appId: string) {
  return useQuery({
    queryKey: ["developer", "apps", appId, "versions"],
    queryFn: async () => {
      const res = await apiWithAuth.get<ListResponse<AppVersion>>(`/api/v1/developer/apps/${appId}/versions`);
      return res.data;
    },
    enabled: !!appId,
  });
}

export function useCreateAppVersion(appId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: CreateAppVersionRequest) => {
      const res = await apiWithAuth.post<DataResponse<AppVersion>>(`/api/v1/developer/apps/${appId}/versions`, data);
      return res.data.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["developer", "apps", appId, "versions"] }),
  });
}

// ── Installations ───────────────────────────────────

export function useOrgInstallations(orgId: string) {
  return useQuery({
    queryKey: ["orgs", orgId, "installations"],
    queryFn: async () => {
      const res = await apiWithAuth.get<ListResponse<AppInstallation>>(`/api/v1/orgs/${orgId}/app-installations`);
      return res.data;
    },
    enabled: !!orgId,
  });
}

// ── API Keys ────────────────────────────────────────

export function useAppApiKeys(appId: string) {
  return useQuery({
    queryKey: ["developer", "apps", appId, "keys"],
    queryFn: async () => {
      const res = await apiWithAuth.get<ListResponse<ApiKey>>(`/api/v1/developer/apps/${appId}/api-keys`);
      return res.data;
    },
    enabled: !!appId,
  });
}

export function useCreateApiKey(appId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: { name: string; scopes?: string[] }) => {
      const res = await apiWithAuth.post<DataResponse<ApiKeyCreated>>(`/api/v1/developer/apps/${appId}/api-keys`, data);
      return res.data.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["developer", "apps", appId, "keys"] }),
  });
}

// ── Marketplace ─────────────────────────────────────

export function useMarketplaceApps(params?: { query?: string; category?: string; page?: number }) {
  return useQuery({
    queryKey: ["marketplace", "apps", params],
    queryFn: async () => {
      const searchParams = new URLSearchParams();
      if (params?.query) searchParams.set("query", params.query);
      if (params?.category) searchParams.set("category", params.category);
      if (params?.page) searchParams.set("page", String(params.page));
      const res = await apiWithAuth.get<ListResponse<AppSummary>>(`/api/v1/marketplace/apps?${searchParams}`);
      return res.data;
    },
  });
}

export function useFeaturedApps() {
  return useQuery({
    queryKey: ["marketplace", "featured"],
    queryFn: async () => {
      const res = await apiWithAuth.get<ListResponse<AppSummary>>("/api/v1/marketplace/featured");
      return res.data;
    },
  });
}
