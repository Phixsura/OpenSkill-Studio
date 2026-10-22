"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface AppInstallDialogProps {
  appId: string;
  appName: string;
  orgId: string;
  permissions: string[];
  onClose: () => void;
  onInstalled?: () => void;
}

/**
 * AppInstallDialog — permission consent + install flow for third-party apps.
 *
 * Shows the app's requested permissions and requires explicit approval
 * before installing into the organization.
 */
export function AppInstallDialog({
  appId,
  appName,
  orgId,
  permissions,
  onClose,
  onInstalled,
}: AppInstallDialogProps) {
  const queryClient = useQueryClient();
  const [selectedPermissions, setSelectedPermissions] = useState<Set<string>>(
    new Set(permissions),
  );
  const [config, setConfig] = useState("{}");
  const [pinVersion, setPinVersion] = useState(false);

  const installMutation = useMutation({
    mutationFn: async () => {
      let parsedConfig = {};
      try {
        parsedConfig = JSON.parse(config);
      } catch {
        /* empty config */
      }
      return apiWithAuth(`/orgs/${orgId}/apps/install`, {
        method: "POST",
        body: JSON.stringify({
          app_id: appId,
          granted_permissions: Array.from(selectedPermissions),
          config: parsedConfig,
          pinned_version: pinVersion,
        }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["org-installations", orgId] });
      onInstalled?.();
      onClose();
    },
  });

  const togglePermission = (perm: string) => {
    const next = new Set(selectedPermissions);
    if (next.has(perm)) {
      next.delete(perm);
    } else {
      next.add(perm);
    }
    setSelectedPermissions(next);
  };

  // Group permissions by category
  const grouped: Record<string, string[]> = {};
  for (const perm of permissions) {
    const action = perm.split(":")[0] ?? "other";
    if (!grouped[action]) grouped[action] = [];
    grouped[action].push(perm);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="mx-4 w-full max-w-lg rounded-xl bg-white p-6 shadow-xl dark:bg-gray-800">
        <h2 className="text-xl font-bold">Install {appName}</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Review the permissions this app requests before installing.
        </p>

        {/* Permissions */}
        <div className="mt-4 max-h-64 overflow-y-auto">
          <h3 className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
            Requested Permissions
          </h3>
          {Object.entries(grouped).map(([category, perms]) => (
            <div key={category} className="mb-3">
              <p className="mb-1 text-xs font-medium uppercase text-gray-400">
                {category}
              </p>
              {perms.map((perm) => (
                <label
                  key={perm}
                  className="flex cursor-pointer items-center gap-2 rounded px-2 py-1 text-sm hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  <input
                    type="checkbox"
                    checked={selectedPermissions.has(perm)}
                    onChange={() => togglePermission(perm)}
                    className="rounded"
                  />
                  <code className="text-xs">{perm}</code>
                </label>
              ))}
            </div>
          ))}
          {permissions.length === 0 && (
            <p className="text-sm text-gray-400">No permissions requested</p>
          )}
        </div>

        {/* Config */}
        <div className="mt-4">
          <label className="mb-1 block text-sm font-medium">
            Configuration (JSON, optional)
          </label>
          <textarea
            className="w-full rounded border px-3 py-2 font-mono text-xs dark:border-gray-600 dark:bg-gray-700"
            value={config}
            onChange={(e) => setConfig(e.target.value)}
            rows={3}
            placeholder="{}"
          />
        </div>

        {/* Pin version */}
        <label className="mt-3 flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={pinVersion}
            onChange={(e) => setPinVersion(e.target.checked)}
            className="rounded"
          />
          Pin to current version (disable auto-updates)
        </label>

        {/* Actions */}
        <div className="mt-6 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() => installMutation.mutate()}
            disabled={installMutation.isPending}
          >
            {installMutation.isPending ? "Installing..." : "Install App"}
          </Button>
        </div>

        {installMutation.isError && (
          <p className="mt-3 text-sm text-red-600">
            {(installMutation.error as Error).message}
          </p>
        )}
      </div>
    </div>
  );
}
