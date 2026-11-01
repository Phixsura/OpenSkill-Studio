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
  installed_by: string;
  status: string;
  granted_permissions: string[];
  config: Record<string, unknown>;
  pinned_version: boolean;
  created_at: string;
  updated_at: string;
}

interface MarketplaceApp {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon_url: string | null;
  category: string;
  visibility: string;
  status: string;
  developer_name: string | null;
  install_count: number;
}

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  suspended: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  uninstalled: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
};

export default function OrgAppsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const queryClient = useQueryClient();
  const [showMarketplace, setShowMarketplace] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Installed apps
  const { data: installsData, isLoading } = useQuery({
    queryKey: ["org-installations", orgId],
    queryFn: () =>
      apiWithAuth<{ data: Installation[]; meta: { total: number } }>(
        `/orgs/${orgId}/apps/installations`,
      ),
  });

  // Marketplace browse
  const { data: marketplaceData } = useQuery({
    queryKey: ["marketplace-apps", searchQuery],
    queryFn: () => {
      const params = new URLSearchParams();
      if (searchQuery) params.set("q", searchQuery);
      params.set("per_page", "20");
      return apiWithAuth<{ data: MarketplaceApp[] }>(`/marketplace/apps?${params.toString()}`);
    },
    enabled: showMarketplace,
  });

  const uninstallMutation = useMutation({
    mutationFn: (installationId: string) =>
      apiWithAuth(`/orgs/${orgId}/apps/installations/${installationId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["org-installations", orgId] });
    },
  });

  const installations = installsData?.data ?? [];
  const marketplaceApps = marketplaceData?.data ?? [];

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Installed Apps</h1>
        <Button onClick={() => setShowMarketplace(!showMarketplace)}>
          {showMarketplace ? "← Back to Installed" : "Browse Marketplace"}
        </Button>
      </div>

      {showMarketplace ? (
        /* Marketplace View */
        <div>
          <div className="mb-4">
            <input
              type="text"
              placeholder="Search apps..."
              className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {marketplaceApps.length === 0 ? (
            <p className="py-12 text-center text-gray-500 dark:text-gray-400">
              No apps available in the marketplace yet.
            </p>
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {marketplaceApps.map((app) => (
                <div key={app.id} className="rounded-lg border p-4 dark:border-gray-700">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold">{app.name}</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        by {app.developer_name ?? "Unknown"}
                      </p>
                      {app.description && (
                        <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                          {app.description.slice(0, 120)}
                          {app.description.length > 120 && "…"}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="mt-3 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <span className="rounded bg-gray-100 px-2 py-0.5 dark:bg-gray-700">
                        {app.category.replace("_", " ")}
                      </span>
                      <span>{app.install_count} installs</span>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        /* Install flow would go here */
                        alert("Install flow: POST /orgs/{orgId}/apps/install with app_id");
                      }}
                    >
                      Install
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        /* Installed Apps View */
        <div>
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-20 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700"
                />
              ))}
            </div>
          ) : installations.length === 0 ? (
            <div className="py-12 text-center text-gray-500 dark:text-gray-400">
              <p className="mb-2 text-lg">No apps installed</p>
              <p className="mb-4 text-sm">
                Browse the marketplace to find apps for your organization
              </p>
              <Button onClick={() => setShowMarketplace(true)}>Browse Marketplace</Button>
            </div>
          ) : (
            <div className="space-y-3">
              {installations.map((inst) => (
                <div key={inst.id} className="rounded-lg border p-4 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold">App {inst.app_id.slice(0, 8)}…</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Installed {new Date(inst.created_at).toLocaleDateString()}
                        {inst.pinned_version && " · Version pinned"}
                      </p>
                      {inst.granted_permissions.length > 0 && (
                        <div className="mt-1 flex flex-wrap gap-1">
                          {inst.granted_permissions.slice(0, 5).map((p) => (
                            <span
                              key={p}
                              className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-700"
                            >
                              {p}
                            </span>
                          ))}
                          {inst.granted_permissions.length > 5 && (
                            <span className="text-xs text-gray-400">
                              +{inst.granted_permissions.length - 5} more
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[inst.status] ?? ""}`}
                      >
                        {inst.status}
                      </span>
                      {inst.status === "active" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            if (confirm("Uninstall this app?")) {
                              uninstallMutation.mutate(inst.id);
                            }
                          }}
                        >
                          Uninstall
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
