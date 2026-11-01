"use client";

import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface AppVersion {
  id: string;
  app_id: string;
  version: string;
  changelog: string | null;
  content_hash: string;
  signature: string | null;
  review_status: string;
  review_notes: string | null;
  min_platform_version: string | null;
  created_at: string;
}

const REVIEW_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  revoked: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
};

export default function AppVersionsPage() {
  const { appId } = useParams<{ appId: string }>();
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    version: "",
    changelog: "",
    content_hash: "",
    signature: "",
    min_platform_version: "",
  });
  const [manifestJson, setManifestJson] = useState(
    JSON.stringify(
      {
        schema_version: "1.0",
        app: { name: "", version: "" },
        permissions: [],
      },
      null,
      2,
    ),
  );
  const [manifestError, setManifestError] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["app-versions", appId],
    queryFn: () =>
      apiWithAuth<{ data: AppVersion[]; meta: { total: number } }>(
        `/developer/apps/${appId}/versions`,
      ),
  });

  const createMutation = useMutation({
    mutationFn: (data: {
      version: string;
      manifest: Record<string, unknown>;
      content_hash: string;
      changelog?: string;
      signature?: string;
      min_platform_version?: string;
    }) =>
      apiWithAuth(`/developer/apps/${appId}/versions`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["app-versions", appId] });
      setShowCreate(false);
      setForm({ version: "", changelog: "", content_hash: "", signature: "", min_platform_version: "" });
    },
  });

  const handleCreate = () => {
    try {
      const manifest = JSON.parse(manifestJson);
      setManifestError("");
      createMutation.mutate({
        version: form.version,
        manifest,
        content_hash: form.content_hash,
        changelog: form.changelog || undefined,
        signature: form.signature || undefined,
        min_platform_version: form.min_platform_version || undefined,
      });
    } catch {
      setManifestError("Invalid JSON in manifest");
    }
  };

  const versions = data?.data ?? [];

  return (
    <div className="max-w-4xl p-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">App Versions</h1>
        <Button onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? "Cancel" : "+ New Version"}
        </Button>
      </div>

      {showCreate && (
        <div className="mb-6 space-y-4 rounded-lg border p-6 dark:border-gray-700">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">Version (semver)</label>
              <input
                type="text"
                className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
                value={form.version}
                onChange={(e) => setForm({ ...form, version: e.target.value })}
                placeholder="1.0.0"
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Content Hash (SHA-256)</label>
              <input
                type="text"
                className="w-full rounded border px-3 py-2 font-mono text-sm dark:border-gray-600 dark:bg-gray-800"
                value={form.content_hash}
                onChange={(e) => setForm({ ...form, content_hash: e.target.value })}
                placeholder="64 hex characters"
                required
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">Manifest (JSON)</label>
            <textarea
              className="w-full rounded border px-3 py-2 font-mono text-sm dark:border-gray-600 dark:bg-gray-800"
              value={manifestJson}
              onChange={(e) => {
                setManifestJson(e.target.value);
                setManifestError("");
              }}
              rows={10}
            />
            {manifestError && <p className="mt-1 text-sm text-red-600">{manifestError}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">Changelog</label>
            <textarea
              className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
              value={form.changelog}
              onChange={(e) => setForm({ ...form, changelog: e.target.value })}
              rows={3}
              placeholder="What changed in this version..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">Signature (optional)</label>
              <input
                type="text"
                className="w-full rounded border px-3 py-2 font-mono text-sm dark:border-gray-600 dark:bg-gray-800"
                value={form.signature}
                onChange={(e) => setForm({ ...form, signature: e.target.value })}
                placeholder="Ed25519 signature"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Min Platform Version</label>
              <input
                type="text"
                className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
                value={form.min_platform_version}
                onChange={(e) => setForm({ ...form, min_platform_version: e.target.value })}
                placeholder="1.0.0"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <Button onClick={handleCreate} disabled={createMutation.isPending}>
              {createMutation.isPending ? "Creating..." : "Create Version"}
            </Button>
            {/* Validate button */}
            <Button
              variant="outline"
              onClick={async () => {
                try {
                  const manifest = JSON.parse(manifestJson);
                  const r = await apiWithAuth<{ data: { valid: boolean; errors: string[]; warnings: string[] } }>(
                    "/developer/validate-manifest",
                    { method: "POST", body: JSON.stringify({ manifest }) },
                  );
                  const v = r.data;
                  if (v.valid) {
                    setManifestError(`✅ Valid${v.warnings.length ? ` (${v.warnings.length} warning(s))` : ""}`);
                  } else {
                    setManifestError(`❌ ${v.errors.length} error(s): ${v.errors.join("; ")}`);
                  }
                } catch {
                  setManifestError("Invalid JSON");
                }
              }}
            >
              Validate Manifest
            </Button>
          </div>
          {createMutation.isError && (
            <p className="text-sm text-red-600">{(createMutation.error as Error).message}</p>
          )}
        </div>
      )}

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2].map((i) => (
            <div key={i} className="h-24 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700" />
          ))}
        </div>
      ) : versions.length === 0 ? (
        <div className="py-12 text-center text-gray-500 dark:text-gray-400">
          <p className="text-lg">No versions yet</p>
          <p className="mt-1 text-sm">Create your first version to start distributing your app</p>
        </div>
      ) : (
        <div className="space-y-3">
          {versions.map((v) => (
            <div key={v.id} className="rounded-lg border p-5 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-lg font-mono font-bold">v{v.version}</span>
                  <span
                    className={`rounded px-2 py-0.5 text-xs font-medium ${REVIEW_COLORS[v.review_status] ?? ""}`}
                  >
                    {v.review_status}
                  </span>
                  {v.signature && (
                    <span className="rounded bg-blue-50 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                      ✍️ Signed
                    </span>
                  )}
                </div>
                <span className="text-sm text-gray-400">
                  {new Date(v.created_at).toLocaleDateString()}
                </span>
              </div>

              {v.changelog && (
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">{v.changelog}</p>
              )}

              <div className="mt-3 flex flex-wrap gap-3 text-xs text-gray-400">
                <span>
                  SHA-256: <code>{v.content_hash.slice(0, 16)}…</code>
                </span>
                {v.min_platform_version && <span>Min platform: {v.min_platform_version}</span>}
              </div>

              {v.review_notes && (
                <div className="mt-3 rounded bg-gray-50 p-3 text-sm dark:bg-gray-800">
                  <span className="font-medium">Review notes:</span> {v.review_notes}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
