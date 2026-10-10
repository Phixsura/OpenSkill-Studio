"use client";

// Integration fabric hub (ADR-018 Part N): connections + health, with
// section links to identity, sync, events and data tooling.
// Credentials are write-only — entered once, never displayed again.

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

interface Provider {
  id: string;
  key: string;
  category: string;
  auth_mode: string;
  display_name: string;
  version: number;
  config_schema: { properties?: Record<string, { description?: string }> };
}

interface Connection {
  id: string;
  provider_key: string;
  provider_version: number;
  name: string;
  status: string;
  base_url: string | null;
  health: { consecutive_failures?: number; last_error_class?: string };
  has_credential: boolean;
}

const SECTIONS = [
  { href: "identity", title: "Identity", desc: "Domains, SSO, SCIM provisioning" },
  { href: "sync", title: "Sync", desc: "Mappings, sync profiles, runs & conflicts" },
  { href: "events", title: "Events", desc: "Event mesh, webhook deliveries, replay" },
  { href: "data", title: "Data", desc: "Bulk imports and warehouse exports" },
];

export default function IntegrationsHubPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const queryClient = useQueryClient();
  const base = `/orgs/${orgId}/integrations`;

  const [providerKey, setProviderKey] = useState("");
  const [name, setName] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [credKind, setCredKind] = useState("api_key");
  const [credValue, setCredValue] = useState("");
  const [credFor, setCredFor] = useState<string | null>(null);

  const { data: providersData, isLoading: providersLoading } = useQuery({
    queryKey: ["intg-providers", orgId],
    queryFn: () => apiWithAuth<{ data: Provider[] }>(`${base}/providers`),
  });
  const providers = providersData?.data ?? [];

  const {
    data: connectionsData,
    isLoading: connectionsLoading,
    isError: connectionsError,
  } = useQuery({
    queryKey: ["intg-connections", orgId],
    queryFn: () => apiWithAuth<{ data: Connection[] }>(`${base}/connections`),
  });
  const connections = connectionsData?.data ?? [];

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["intg-connections", orgId] });

  const createConnection = useMutation({
    mutationFn: () =>
      apiWithAuth(`${base}/connections`, {
        method: "POST",
        body: JSON.stringify({
          provider_key: providerKey,
          name,
          config: {},
          base_url: baseUrl || null,
        }),
      }),
    onSuccess: () => {
      toast.success("Connection created");
      setName("");
      setBaseUrl("");
      invalidate();
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Failed to create connection"),
  });

  const ping = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth<{ data: { ok: boolean; status: string; detail?: string } }>(
        `${base}/connections/${id}/ping`,
        { method: "POST" },
      ),
    onSuccess: (res) => {
      if (res.data.ok) toast.success(`Connection healthy (${res.data.status})`);
      else toast.error(`Ping failed: ${res.data.detail ?? "unknown"}`);
      invalidate();
    },
    onError: () => toast.error("Ping failed"),
  });

  const saveCredential = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth(`${base}/connections/${id}/credentials`, {
        method: "POST",
        body: JSON.stringify({ kind: credKind, values: { api_key: credValue } }),
      }),
    onSuccess: () => {
      toast.success("Credential stored (write-only)");
      setCredFor(null);
      setCredValue("");
      invalidate();
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Failed to store credential"),
  });

  const upgradeConnection = useMutation({
    mutationFn: (id: string) =>
      apiWithAuth(`${base}/connections/${id}/upgrade`, { method: "POST" }),
    onSuccess: () => {
      toast.success("Connection upgraded to the current provider version");
      invalidate();
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Upgrade failed"),
  });

  const removeConnection = useMutation({
    mutationFn: (id: string) => apiWithAuth(`${base}/connections/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      toast.success("Connection deleted");
      invalidate();
    },
    onError: () => toast.error("Failed to delete connection"),
  });

  return (
    <div className="space-y-8 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Integrations</h1>
        <p className="text-muted-foreground text-sm">
          Connect identity, roster, talent and data systems. Credentials are stored encrypted and
          never shown again.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {SECTIONS.map((s) => (
          <Link
            key={s.href}
            href={`/dashboard/orgs/${orgId}/integrations/${s.href}`}
            className="hover:bg-accent rounded-lg border p-4"
          >
            <div className="font-medium">{s.title}</div>
            <div className="text-muted-foreground text-sm">{s.desc}</div>
          </Link>
        ))}
      </div>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">Connections</h2>
        {connectionsLoading && <p>Loading connections…</p>}
        {connectionsError && <p className="text-destructive">Failed to load connections.</p>}
        {!connectionsLoading && connections.length === 0 && (
          <p className="text-muted-foreground text-sm">No connections yet.</p>
        )}
        <ul className="space-y-2">
          {connections.map((c) => (
            <li key={c.id} className="rounded-md border p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <span className="font-medium">{c.name}</span>{" "}
                  <span className="text-muted-foreground text-xs">({c.provider_key})</span>
                  <span
                    className={`ml-2 rounded px-2 py-0.5 text-xs ${
                      c.status === "active"
                        ? "bg-green-100 text-green-800"
                        : c.status === "error" || c.status === "degraded"
                          ? "bg-red-100 text-red-800"
                          : "bg-gray-100 text-gray-800"
                    }`}
                  >
                    {c.status}
                  </span>
                  {!c.has_credential && (
                    <span className="ml-2 text-xs text-amber-700">no credential</span>
                  )}
                  {c.health?.last_error_class && (
                    <span className="ml-2 text-xs text-red-700">{c.health.last_error_class}</span>
                  )}
                </div>
                <div className="flex gap-2">
                  {(providers.find((p) => p.key === c.provider_key)?.version ?? 0) >
                    c.provider_version && (
                    <Button size="sm" onClick={() => upgradeConnection.mutate(c.id)}>
                      Upgrade
                    </Button>
                  )}
                  <Button size="sm" variant="outline" onClick={() => ping.mutate(c.id)}>
                    Ping
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setCredFor(credFor === c.id ? null : c.id)}
                  >
                    Set credential
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => removeConnection.mutate(c.id)}
                  >
                    Delete
                  </Button>
                </div>
              </div>
              {credFor === c.id && (
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <select
                    aria-label="Credential kind"
                    className="rounded-md border px-2 py-1 text-sm"
                    value={credKind}
                    onChange={(e) => setCredKind(e.target.value)}
                  >
                    <option value="api_key">API key</option>
                    <option value="oauth2_tokens">OAuth2 client</option>
                    <option value="basic">Basic</option>
                  </select>
                  <Input
                    aria-label="Credential value"
                    type="password"
                    placeholder="Secret value (write-only)"
                    value={credValue}
                    onChange={(e) => setCredValue(e.target.value)}
                    className="max-w-xs"
                  />
                  <Button
                    size="sm"
                    disabled={!credValue || saveCredential.isPending}
                    onClick={() => saveCredential.mutate(c.id)}
                  >
                    Save
                  </Button>
                </div>
              )}
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-3 rounded-lg border p-4">
        <h2 className="text-lg font-medium">New connection</h2>
        <div className="flex flex-wrap items-end gap-3">
          <label className="flex flex-col gap-1 text-sm">
            Provider
            <select
              aria-label="Provider"
              className="rounded-md border px-2 py-1"
              value={providerKey}
              onChange={(e) => setProviderKey(e.target.value)}
            >
              <option value="">Select…</option>
              {providers.map((p) => (
                <option key={p.key} value={p.key}>
                  {p.display_name} ({p.category})
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            Name
            <Input
              aria-label="Connection name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="District SIS"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            Base URL
            <Input
              aria-label="Base URL"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              placeholder="https://…"
            />
          </label>
          <Button
            disabled={!providerKey || !name || createConnection.isPending || providersLoading}
            onClick={() => createConnection.mutate()}
          >
            Create
          </Button>
        </div>
      </section>
    </div>
  );
}
