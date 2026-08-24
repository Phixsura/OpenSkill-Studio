"use client";

// Provider management (ADR-011): connections + offerings.
// Credentials are write-only — entered once, stored encrypted, never shown again.

import { useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

interface Adapter {
  id: string;
  key: string;
  name: string;
  credential_fields: string[];
}

interface Connection {
  id: string;
  adapter_id: string;
  name: string;
  status: string;
  health_status: string | null;
  credential_id: string | null;
}

interface Capability {
  key: string;
  name: string;
}

interface Offering {
  id: string;
  connection_id: string;
  capability_key: string;
  model_name: string;
  quality_tier: string;
  cost_per_call_usd: number | null;
  is_active: boolean;
}

export default function ProvidersPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const queryClient = useQueryClient();

  const [newAdapterId, setNewAdapterId] = useState("");
  const [newName, setNewName] = useState("");
  const [credValues, setCredValues] = useState<Record<string, string>>({});
  const [armedDelete, setArmedDelete] = useState<string | null>(null);

  const [offConnection, setOffConnection] = useState("");
  const [offCapability, setOffCapability] = useState("");
  const [offModel, setOffModel] = useState("");
  const [offTier, setOffTier] = useState("standard");
  const [offCost, setOffCost] = useState("");

  const { data: adaptersData } = useQuery({
    queryKey: ["provider-adapters"],
    queryFn: () => apiWithAuth<{ data: Adapter[] }>("/providers/adapters"),
  });
  const adapters = adaptersData?.data ?? [];
  const selectedAdapter = adapters.find((a) => a.id === newAdapterId);

  const { data: capsData } = useQuery({
    queryKey: ["capabilities"],
    queryFn: () => apiWithAuth<{ data: Capability[] }>("/capabilities"),
  });
  const capabilities = capsData?.data ?? [];

  const { data: connectionsData } = useQuery({
    queryKey: ["provider-connections", orgId],
    queryFn: () => apiWithAuth<{ data: Connection[] }>(`/orgs/${orgId}/provider-connections`),
  });
  const connections = connectionsData?.data ?? [];

  const { data: offeringsData } = useQuery({
    queryKey: ["provider-offerings", orgId],
    queryFn: () => apiWithAuth<{ data: Offering[] }>(`/orgs/${orgId}/provider-offerings`),
  });
  const offerings = offeringsData?.data ?? [];

  const createConnection = useMutation({
    mutationFn: () => {
      const credentials = Object.fromEntries(
        Object.entries(credValues).filter(([, v]) => v.trim()),
      );
      return apiWithAuth(`/orgs/${orgId}/provider-connections`, {
        method: "POST",
        body: JSON.stringify({
          adapter_id: newAdapterId,
          name: newName,
          credentials: Object.keys(credentials).length ? credentials : null,
        }),
      });
    },
    onSuccess: () => {
      toast.success("Provider connected");
      setNewName("");
      setNewAdapterId("");
      setCredValues({});
      queryClient.invalidateQueries({ queryKey: ["provider-connections", orgId] });
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Connection failed"),
  });

  const deleteConnection = useMutation({
    mutationFn: (connectionId: string) =>
      apiWithAuth(`/orgs/${orgId}/provider-connections/${connectionId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      toast.success("Connection removed");
      setArmedDelete(null);
      queryClient.invalidateQueries({ queryKey: ["provider-connections", orgId] });
      queryClient.invalidateQueries({ queryKey: ["provider-offerings", orgId] });
    },
    onError: (err) => {
      setArmedDelete(null);
      toast.error(err instanceof ApiError ? err.message : "Delete failed");
    },
  });

  const createOffering = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/provider-offerings`, {
        method: "POST",
        body: JSON.stringify({
          connection_id: offConnection,
          capability_key: offCapability,
          model_name: offModel,
          quality_tier: offTier,
          // Cost drives binding auto-suggestion ranking ("cheapest active
          // offering") — optional but should be settable from the UI
          cost_per_call_usd: offCost ? Number(offCost) : undefined,
        }),
      }),
    onSuccess: () => {
      toast.success("Offering added");
      setOffModel("");
      setOffCost("");
      queryClient.invalidateQueries({ queryKey: ["provider-offerings", orgId] });
    },
    onError: (err) => toast.error(err instanceof ApiError ? err.message : "Failed to add offering"),
  });

  const deleteOffering = useMutation({
    mutationFn: (offeringId: string) =>
      apiWithAuth(`/orgs/${orgId}/provider-offerings/${offeringId}`, { method: "DELETE" }),
    onSuccess: () => {
      toast.success("Offering removed");
      queryClient.invalidateQueries({ queryKey: ["provider-offerings", orgId] });
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Failed to remove offering"),
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Providers</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Connect AI providers and declare which capabilities each model offers. Workflows bind to
          capabilities, never to vendors.
        </p>
      </div>

      {/* Connections */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Connections</h2>
        {connections.length === 0 && (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            No provider connections yet.
          </p>
        )}
        <div className="space-y-2">
          {connections.map((conn) => {
            const adapter = adapters.find((a) => a.id === conn.adapter_id);
            const connOfferings = offerings.filter((o) => o.connection_id === conn.id);
            return (
              <div key={conn.id} className="rounded-lg border p-4">
                <div className="flex items-center gap-3">
                  <span className="font-medium">{conn.name}</span>
                  <span className="text-xs text-[hsl(var(--muted-foreground))]">
                    {adapter?.name ?? conn.adapter_id}
                  </span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      conn.status === "active"
                        ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                        : "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300"
                    }`}
                  >
                    {conn.status}
                  </span>
                  {conn.credential_id && (
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">
                      🔒 credentials stored
                    </span>
                  )}
                  <div className="ml-auto">
                    {armedDelete === conn.id ? (
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => deleteConnection.mutate(conn.id)}
                          disabled={deleteConnection.isPending}
                        >
                          Confirm delete?
                        </Button>
                        <Button size="sm" variant="secondary" onClick={() => setArmedDelete(null)}>
                          Cancel
                        </Button>
                      </div>
                    ) : (
                      <Button size="sm" variant="secondary" onClick={() => setArmedDelete(conn.id)}>
                        Delete
                      </Button>
                    )}
                  </div>
                </div>
                {connOfferings.length > 0 && (
                  <table className="mt-3 w-full text-sm">
                    <thead>
                      <tr className="text-left text-xs text-[hsl(var(--muted-foreground))]">
                        <th className="py-1 font-medium">Capability</th>
                        <th className="py-1 font-medium">Model</th>
                        <th className="py-1 font-medium">Tier</th>
                        <th className="py-1 font-medium">Cost/call</th>
                        <th className="py-1 font-medium">Active</th>
                        <th className="py-1" />
                      </tr>
                    </thead>
                    <tbody>
                      {connOfferings.map((o) => (
                        <tr key={o.id} className="border-t">
                          <td className="py-1.5">{o.capability_key}</td>
                          <td className="py-1.5">{o.model_name}</td>
                          <td className="py-1.5">{o.quality_tier}</td>
                          <td className="py-1.5">
                            {o.cost_per_call_usd != null ? `$${o.cost_per_call_usd}` : "—"}
                          </td>
                          <td className="py-1.5">{o.is_active ? "✓" : "—"}</td>
                          <td className="py-1.5 text-right">
                            <Button
                              size="sm"
                              variant="ghost"
                              aria-label={`Remove offering ${o.model_name}`}
                              disabled={deleteOffering.isPending}
                              onClick={() => deleteOffering.mutate(o.id)}
                            >
                              Remove
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            );
          })}
        </div>

        {/* New connection */}
        <div className="space-y-3 rounded-lg border border-dashed p-4">
          <h3 className="text-sm font-semibold">Connect a provider</h3>
          <div className="grid gap-3 sm:grid-cols-2">
            <select
              value={newAdapterId}
              onChange={(e) => {
                setNewAdapterId(e.target.value);
                setCredValues({});
              }}
              className="rounded-md border bg-transparent px-3 py-2 text-sm"
              aria-label="Provider adapter"
            >
              <option value="">Select adapter…</option>
              {adapters.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
            <Input
              placeholder="Connection name"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              maxLength={100}
            />
          </div>
          {selectedAdapter && selectedAdapter.credential_fields.length > 0 && (
            <div className="space-y-2">
              {selectedAdapter.credential_fields.map((field) => (
                <div key={field} className="space-y-1">
                  <label htmlFor={`cred-${field}`} className="text-xs font-medium">
                    {field}
                  </label>
                  <Input
                    id={`cred-${field}`}
                    type="password"
                    autoComplete="off"
                    value={credValues[field] ?? ""}
                    onChange={(e) =>
                      setCredValues((prev) => ({ ...prev, [field]: e.target.value }))
                    }
                  />
                </div>
              ))}
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                Stored encrypted; never shown again.
              </p>
            </div>
          )}
          <Button
            size="sm"
            onClick={() => createConnection.mutate()}
            disabled={!newAdapterId || !newName.trim() || createConnection.isPending}
          >
            {createConnection.isPending ? "Connecting..." : "Connect"}
          </Button>
        </div>
      </section>

      {/* Add offering */}
      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Add Offering</h2>
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Declare a model on a connection as providing a capability — this is what workflow steps
          bind to.
        </p>
        <div className="grid gap-3 sm:grid-cols-4">
          <select
            value={offConnection}
            onChange={(e) => setOffConnection(e.target.value)}
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            aria-label="Connection"
          >
            <option value="">Connection…</option>
            {connections.map((conn) => (
              <option key={conn.id} value={conn.id}>
                {conn.name}
              </option>
            ))}
          </select>
          <select
            value={offCapability}
            onChange={(e) => setOffCapability(e.target.value)}
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            aria-label="Capability"
          >
            <option value="">Capability…</option>
            {capabilities.map((cap) => (
              <option key={cap.key} value={cap.key}>
                {cap.name}
              </option>
            ))}
          </select>
          <Input
            placeholder="Model name"
            value={offModel}
            onChange={(e) => setOffModel(e.target.value)}
            maxLength={200}
          />
          <select
            value={offTier}
            onChange={(e) => setOffTier(e.target.value)}
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            aria-label="Quality tier"
          >
            <option value="draft">Draft</option>
            <option value="standard">Standard</option>
            <option value="premium">Premium</option>
          </select>
          <Input
            type="number"
            min={0}
            max={10000}
            step="0.000001"
            placeholder="Cost per call USD (optional)"
            aria-label="Cost per call USD"
            value={offCost}
            onChange={(e) => setOffCost(e.target.value)}
          />
        </div>
        <Button
          size="sm"
          onClick={() => createOffering.mutate()}
          disabled={
            !offConnection || !offCapability || !offModel.trim() || createOffering.isPending
          }
        >
          {createOffering.isPending ? "Adding..." : "Add Offering"}
        </Button>
      </section>
    </div>
  );
}
