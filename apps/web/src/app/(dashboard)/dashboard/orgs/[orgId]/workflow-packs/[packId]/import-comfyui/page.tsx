"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

interface DependencyReport {
  custom_nodes: { class_type: string; count: number }[];
  models: { filename: string; node_type: string; confidence: string }[];
  input_nodes: string[];
  output_nodes: string[];
  capabilities_detected: string[];
  total_nodes: number;
  custom_node_count: number;
}

interface ImportResult {
  id: string;
  format_detected: string;
  status: string;
  dependency_report: DependencyReport;
  original_sha256: string;
  pack_id: string | null;
  created_at: string;
}

export default function ImportComfyUIPage() {
  const { orgId } = useParams<{ orgId: string; packId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [currentImport, setCurrentImport] = useState<ImportResult | null>(null);
  const [draftName, setDraftName] = useState("");

  const { data: importsData } = useQuery({
    queryKey: ["comfyui-imports", orgId],
    queryFn: () =>
      apiWithAuth<{ data: ImportResult[] }>(`/orgs/${orgId}/comfyui-imports`),
  });

  const importMutation = useMutation({
    mutationFn: (payload: { data: string; encoding: string }) =>
      apiWithAuth<{ data: ImportResult }>(`/orgs/${orgId}/comfyui-imports`, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: (res) => {
      setCurrentImport(res.data);
      queryClient.invalidateQueries({ queryKey: ["comfyui-imports", orgId] });
      toast.success("Workflow imported and analyzed");
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Import failed"),
  });

  const createPackMutation = useMutation({
    mutationFn: (importId: string) =>
      apiWithAuth<{ data: { id: string } }>(
        `/orgs/${orgId}/comfyui-imports/${importId}/create-pack`,
        { method: "POST", body: JSON.stringify({ name: draftName }) },
      ),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["workflow-packs", orgId] });
      toast.success("Draft pack created");
      router.push(`/dashboard/orgs/${orgId}/workflow-packs/${res.data.id}`);
    },
    onError: (err) =>
      toast.error(err instanceof ApiError ? err.message : "Pack creation failed"),
  });

  const handleFile = async (file: File) => {
    if (file.name.endsWith(".json")) {
      const text = await file.text();
      importMutation.mutate({ data: text, encoding: "json" });
    } else if (file.name.endsWith(".png")) {
      const reader = new FileReader();
      reader.onload = () => {
        const dataUrl = String(reader.result ?? "");
        const base64 = dataUrl.split(",")[1] ?? "";
        importMutation.mutate({ data: base64, encoding: "base64" });
      };
      reader.readAsDataURL(file);
    } else {
      toast.error("Only .json and .png files are supported");
    }
  };

  const report = currentImport?.dependency_report;
  const previousImports = importsData?.data ?? [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Import ComfyUI Workflow</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Upload a ComfyUI workflow JSON or a PNG with embedded metadata. The
          workflow is parsed and inspected only — never executed.
        </p>
      </div>

      <div className="rounded-lg border border-dashed p-8 text-center">
        <label htmlFor="comfy-file" className="block text-sm font-medium">
          Workflow file (.json or .png)
        </label>
        <input
          id="comfy-file"
          type="file"
          accept=".json,.png"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
            // Reset so re-selecting the same file retriggers (e.g. retry
            // after a transient import failure)
            e.target.value = "";
          }}
          className="mx-auto mt-3 block text-sm"
        />
        {importMutation.isPending && (
          <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">Analyzing…</p>
        )}
      </div>

      {currentImport && report && (
        <section className="space-y-4">
          <h2 className="text-xl font-semibold">Dependency Report</h2>
          <div className="rounded-lg border p-4">
            <p className="text-sm">
              Format: <span className="font-mono">{currentImport.format_detected}</span>{" "}
              · {report.total_nodes} nodes · {report.custom_node_count} custom
            </p>

            {report.capabilities_detected.length > 0 && (
              <div className="mt-3">
                <h3 className="text-sm font-medium">Detected capabilities</h3>
                <div className="mt-1 flex flex-wrap gap-1">
                  {report.capabilities_detected.map((cap) => (
                    <span
                      key={cap}
                      className="rounded bg-emerald-100 px-2 py-0.5 text-xs text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200"
                    >
                      {cap}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {report.custom_nodes.length > 0 && (
              <div className="mt-3">
                <h3 className="text-sm font-medium">
                  Custom nodes ({report.custom_nodes.length}) — unresolved dependencies
                </h3>
                <table className="mt-1 w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs text-[hsl(var(--muted-foreground))]">
                      <th className="py-1">Node class</th>
                      <th className="py-1">Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.custom_nodes.map((node) => (
                      <tr key={node.class_type} className="border-t">
                        <td className="py-1 font-mono text-xs">{node.class_type}</td>
                        <td className="py-1">{node.count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {report.models.length > 0 && (
              <div className="mt-3">
                <h3 className="text-sm font-medium">Model files ({report.models.length})</h3>
                <table className="mt-1 w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs text-[hsl(var(--muted-foreground))]">
                      <th className="py-1">File</th>
                      <th className="py-1">Node</th>
                      <th className="py-1">Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.models.map((model, i) => (
                      <tr key={i} className="border-t">
                        <td className="py-1 font-mono text-xs">{model.filename}</td>
                        <td className="py-1 text-xs">{model.node_type}</td>
                        <td className="py-1">
                          <span
                            className={`rounded px-1.5 py-0.5 text-[10px] ${
                              model.confidence === "whitelist"
                                ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                                : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                            }`}
                          >
                            {model.confidence}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
              <p>Input nodes: {report.input_nodes.join(", ") || "none detected"}</p>
              <p>Output nodes: {report.output_nodes.join(", ") || "none detected"}</p>
            </div>
          </div>

          <div className="flex items-end gap-2 rounded-lg border p-4">
            <div className="flex-1">
              <label htmlFor="draft-name" className="block text-sm font-medium">
                Draft pack name
              </label>
              <Input
                id="draft-name"
                value={draftName}
                onChange={(e) => setDraftName(e.target.value)}
                placeholder="Imported ComfyUI Workflow"
                className="mt-1"
              />
            </div>
            <Button
              disabled={!draftName.trim() || createPackMutation.isPending}
              onClick={() => createPackMutation.mutate(currentImport.id)}
            >
              {createPackMutation.isPending ? "Creating…" : "Create Draft Pack"}
            </Button>
          </div>
        </section>
      )}

      {previousImports.length > 0 && (
        <section>
          <h2 className="text-xl font-semibold">Previous Imports</h2>
          <div className="mt-3 space-y-2">
            {previousImports.map((imp) => (
              <div
                key={imp.id}
                className="flex items-center justify-between rounded-lg border px-4 py-2 text-sm"
              >
                <span className="font-mono text-xs">{imp.original_sha256.slice(0, 12)}…</span>
                <span>{imp.format_detected}</span>
                <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
                  {imp.status}
                </span>
                {imp.pack_id ? (
                  <Link
                    href={`/dashboard/orgs/${orgId}/workflow-packs/${imp.pack_id}`}
                    className="text-xs text-[hsl(var(--primary))] hover:underline"
                  >
                    View pack
                  </Link>
                ) : (
                  <button
                    onClick={() => setCurrentImport(imp)}
                    className="text-xs hover:underline"
                  >
                    View report
                  </button>
                )}
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  {new Date(imp.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
