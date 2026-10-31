"use client";

import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface Installation {
  id: string;
  app_id: string;
  app_version_id: string;
  org_id: string;
  status: string;
  granted_permissions: string[];
  config: Record<string, unknown>;
  pinned_version: boolean;
  created_at: string;
}

interface SecretMeta {
  id: string;
  installation_id: string;
  key: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

interface EventSub {
  id: string;
  installation_id: string;
  event_type: string;
  enabled: boolean;
  created_at: string;
}

interface AutoRule {
  id: string;
  name: string;
  trigger_event: string;
  action_type: string;
  enabled: boolean;
  execution_count: number;
}

export default function InstallationDetailPage() {
  const { orgId, installationId } = useParams<{ orgId: string; installationId: string }>();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"overview" | "secrets" | "events" | "rules">("overview");
  const [newSecret, setNewSecret] = useState({ key: "", value: "", description: "" });
  const [newEvent, setNewEvent] = useState("");

  const { data: inst } = useQuery({
    queryKey: ["installation", orgId, installationId],
    queryFn: () =>
      apiWithAuth<{ data: Installation }>(
        `/orgs/${orgId}/apps/installations/${installationId}`,
      ).then((r) => r.data),
  });

  const { data: secretsData } = useQuery({
    queryKey: ["installation-secrets", installationId],
    queryFn: () =>
      apiWithAuth<{ data: SecretMeta[] }>(
        `/orgs/${orgId}/apps/installations/${installationId}/secrets`,
      ),
    enabled: activeTab === "secrets",
  });

  const { data: eventsData } = useQuery({
    queryKey: ["installation-events", installationId],
    queryFn: () =>
      apiWithAuth<{ data: EventSub[] }>(
        `/orgs/${orgId}/apps/installations/${installationId}/events`,
      ),
    enabled: activeTab === "events",
  });

  const { data: rulesData } = useQuery({
    queryKey: ["installation-rules", installationId],
    queryFn: () =>
      apiWithAuth<{ data: AutoRule[] }>(
        `/orgs/${orgId}/apps/installations/${installationId}/rules`,
      ),
    enabled: activeTab === "rules",
  });

  const setSecretMut = useMutation({
    mutationFn: (data: { key: string; value: string; description?: string }) =>
      apiWithAuth(`/orgs/${orgId}/apps/installations/${installationId}/secrets`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["installation-secrets", installationId] });
      setNewSecret({ key: "", value: "", description: "" });
    },
  });

  const addEventMut = useMutation({
    mutationFn: (eventType: string) =>
      apiWithAuth(`/orgs/${orgId}/apps/installations/${installationId}/events`, {
        method: "POST",
        body: JSON.stringify({ event_type: eventType }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["installation-events", installationId] });
      setNewEvent("");
    },
  });

  const upgradeMut = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/apps/installations/${installationId}/upgrade`, {
        method: "POST",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["installation", orgId, installationId] });
    },
  });

  if (!inst) {
    return (
      <div className="p-8">
        <div className="h-8 w-48 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
      </div>
    );
  }

  const secrets = secretsData?.data ?? [];
  const events = eventsData?.data ?? [];
  const rules = rulesData?.data ?? [];

  return (
    <div className="max-w-4xl p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Installation Details</h1>
          <p className="mt-1 text-sm text-gray-500">App: {inst.app_id.slice(0, 12)}…</p>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => upgradeMut.mutate()}>
            ⬆ Upgrade
          </Button>
          <span
            className={`rounded px-3 py-1 text-sm font-medium ${
              inst.status === "active"
                ? "bg-green-100 text-green-800"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            {inst.status}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 border-b dark:border-gray-700">
        {(["overview", "secrets", "events", "rules"] as const).map((tab) => (
          <button
            key={tab}
            className={`border-b-2 px-4 py-2 text-sm font-medium ${
              activeTab === tab
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Overview */}
      {activeTab === "overview" && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-lg border p-4 dark:border-gray-700">
              <p className="text-sm text-gray-500">Version</p>
              <p className="font-mono text-sm">{inst.app_version_id.slice(0, 12)}…</p>
            </div>
            <div className="rounded-lg border p-4 dark:border-gray-700">
              <p className="text-sm text-gray-500">Pinned</p>
              <p>{inst.pinned_version ? "Yes" : "No (auto-update)"}</p>
            </div>
          </div>
          {inst.granted_permissions.length > 0 && (
            <div className="rounded-lg border p-4 dark:border-gray-700">
              <p className="mb-2 text-sm font-medium text-gray-500">Granted Permissions</p>
              <div className="flex flex-wrap gap-1">
                {inst.granted_permissions.map((p) => (
                  <span key={p} className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-700">
                    {p}
                  </span>
                ))}
              </div>
            </div>
          )}
          {Object.keys(inst.config).length > 0 && (
            <div className="rounded-lg border p-4 dark:border-gray-700">
              <p className="mb-2 text-sm font-medium text-gray-500">Configuration</p>
              <pre className="rounded bg-gray-50 p-3 text-xs dark:bg-gray-800">
                {JSON.stringify(inst.config, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Secrets */}
      {activeTab === "secrets" && (
        <div className="space-y-4">
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <h3 className="mb-3 font-medium">Add Secret</h3>
            <div className="grid grid-cols-3 gap-2">
              <input
                placeholder="KEY_NAME"
                className="rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800"
                value={newSecret.key}
                onChange={(e) => setNewSecret({ ...newSecret, key: e.target.value.toUpperCase() })}
              />
              <input
                placeholder="value"
                type="password"
                className="rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800"
                value={newSecret.value}
                onChange={(e) => setNewSecret({ ...newSecret, value: e.target.value })}
              />
              <Button
                size="sm"
                onClick={() => setSecretMut.mutate(newSecret)}
                disabled={!newSecret.key || !newSecret.value}
              >
                Set
              </Button>
            </div>
          </div>
          {secrets.map((s) => (
            <div key={s.id} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
              <div>
                <span className="font-mono text-sm font-medium">{s.key}</span>
                {s.description && (
                  <span className="ml-2 text-xs text-gray-400">{s.description}</span>
                )}
              </div>
              <span className="text-xs text-gray-400">
                {new Date(s.updated_at).toLocaleDateString()}
              </span>
            </div>
          ))}
          {secrets.length === 0 && (
            <p className="py-4 text-center text-sm text-gray-400">No secrets configured</p>
          )}
        </div>
      )}

      {/* Events */}
      {activeTab === "events" && (
        <div className="space-y-4">
          <div className="flex gap-2">
            <input
              placeholder="e.g. submission.completed"
              className="flex-1 rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
              value={newEvent}
              onChange={(e) => setNewEvent(e.target.value)}
            />
            <Button size="sm" onClick={() => addEventMut.mutate(newEvent)} disabled={!newEvent}>
              Subscribe
            </Button>
          </div>
          {events.map((ev) => (
            <div key={ev.id} className="flex items-center justify-between rounded border p-3 dark:border-gray-700">
              <span className="font-mono text-sm">{ev.event_type}</span>
              <span className={`text-xs ${ev.enabled ? "text-green-600" : "text-gray-400"}`}>
                {ev.enabled ? "Active" : "Disabled"}
              </span>
            </div>
          ))}
          {events.length === 0 && (
            <p className="py-4 text-center text-sm text-gray-400">No event subscriptions</p>
          )}
        </div>
      )}

      {/* Rules */}
      {activeTab === "rules" && (
        <div className="space-y-3">
          {rules.map((rule) => (
            <div key={rule.id} className="rounded-lg border p-4 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <span className="font-medium">{rule.name}</span>
                <span className={`text-xs ${rule.enabled ? "text-green-600" : "text-gray-400"}`}>
                  {rule.enabled ? "Enabled" : "Disabled"}
                </span>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                When: <code>{rule.trigger_event}</code> → Action: {rule.action_type}
              </p>
              <p className="mt-1 text-xs text-gray-400">
                Executed {rule.execution_count} time(s)
              </p>
            </div>
          ))}
          {rules.length === 0 && (
            <p className="py-8 text-center text-sm text-gray-400">No automation rules configured</p>
          )}
        </div>
      )}
    </div>
  );
}
