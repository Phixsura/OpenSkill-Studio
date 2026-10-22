"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

export default function AppExportPage() {
  const { appId } = useParams<{ appId: string }>();
  const [exported, setExported] = useState(false);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["app-export", appId],
    queryFn: () =>
      apiWithAuth<{ data: Record<string, unknown> }>(
        `/developer/apps/${appId}/export`,
      ).then((r) => r.data),
    enabled: exported,
  });

  const handleExport = () => {
    setExported(true);
    refetch();
  };

  const handleDownload = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `app-export-${appId.slice(0, 8)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-4xl p-8">
      <h1 className="mb-2 text-2xl font-bold">Export App</h1>
      <p className="mb-6 text-sm text-gray-500 dark:text-gray-400">
        Export your app configuration for backup or migration to another environment
      </p>

      {!exported ? (
        <div className="rounded-lg border p-8 text-center dark:border-gray-700">
          <p className="mb-4 text-gray-600 dark:text-gray-400">
            The export includes app metadata, all versions with manifests, and UI extension
            configurations. It does NOT include installation-specific data or secrets.
          </p>
          <Button onClick={handleExport}>Generate Export</Button>
        </div>
      ) : isLoading ? (
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-64 rounded-lg bg-gray-200 dark:bg-gray-700" />
        </div>
      ) : data ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              Exported: {(data as Record<string, unknown>).exported_at as string}
            </div>
            <Button onClick={handleDownload}>⬇ Download JSON</Button>
          </div>
          <pre className="max-h-96 overflow-auto rounded-lg bg-gray-900 p-4 text-xs text-gray-100">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      ) : null}
    </div>
  );
}
