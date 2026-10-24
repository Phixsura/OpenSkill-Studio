"use client";

import { useParams } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";
import { CompatibilityReport } from "@/components/compatibility-report";

interface AppVersion {
  id: string;
  version: string;
}

export default function CompatibilityPage() {
  const { appId } = useParams<{ appId: string }>();
  const [fromVersion, setFromVersion] = useState("");
  const [toVersion, setToVersion] = useState("");

  const { data: versionsData } = useQuery({
    queryKey: ["app-versions", appId],
    queryFn: () =>
      apiWithAuth<{ data: AppVersion[] }>(`/developer/apps/${appId}/versions`),
  });

  const checkMutation = useMutation({
    mutationFn: (params: { current_version_id: string; new_version_id: string }) =>
      apiWithAuth<{
        data: {
          from_version: string;
          to_version: string;
          compatible: boolean;
          breaking_changes: string[];
          warnings: string[];
          permissions_added: string[];
          permissions_removed: string[];
        };
      }>(`/developer/apps/${appId}/check-compatibility`, {
        method: "POST",
        body: JSON.stringify(params),
      }).then((r) => r.data),
  });

  const versions = versionsData?.data ?? [];

  return (
    <div className="max-w-4xl p-8">
      <h1 className="mb-2 text-2xl font-bold">Compatibility Check</h1>
      <p className="mb-6 text-sm text-gray-500 dark:text-gray-400">
        Compare two versions to check for breaking changes before upgrading installations
      </p>

      <div className="mb-6 rounded-lg border p-6 dark:border-gray-700">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium">From Version</label>
            <select
              className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
              value={fromVersion}
              onChange={(e) => setFromVersion(e.target.value)}
            >
              <option value="">Select...</option>
              {versions.map((v) => (
                <option key={v.id} value={v.id}>
                  v{v.version}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">To Version</label>
            <select
              className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
              value={toVersion}
              onChange={(e) => setToVersion(e.target.value)}
            >
              <option value="">Select...</option>
              {versions.map((v) => (
                <option key={v.id} value={v.id}>
                  v{v.version}
                </option>
              ))}
            </select>
          </div>
        </div>
        <Button
          className="mt-4"
          onClick={() =>
            checkMutation.mutate({
              current_version_id: fromVersion,
              new_version_id: toVersion,
            })
          }
          disabled={!fromVersion || !toVersion || checkMutation.isPending}
        >
          {checkMutation.isPending ? "Checking..." : "Check Compatibility"}
        </Button>
      </div>

      {checkMutation.data && <CompatibilityReport report={checkMutation.data} />}

      {checkMutation.isError && (
        <p className="text-sm text-red-600">
          {(checkMutation.error as Error).message}
        </p>
      )}
    </div>
  );
}
