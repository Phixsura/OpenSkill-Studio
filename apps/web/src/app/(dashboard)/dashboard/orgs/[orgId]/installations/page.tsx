"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface Install {
  id: string;
  org_id: string;
  pack_id: string | null;
  release_id: string | null;
  installed_version: string;
  status: string;
  installed_by: string;
  installed_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  forked: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  removed: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
};

export default function InstallationsListPage() {
  const { orgId } = useParams<{ orgId: string }>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["installations", orgId],
    queryFn: () =>
      apiWithAuth<{ data: Install[]; meta: { total: number } }>(
        `/orgs/${orgId}/installations`,
      ),
  });

  const installations = data?.data ?? [];

  return (
    <div className="space-y-6">
      {isError && (
        <p className="mb-4 text-sm text-red-600">
          Failed to load installations. Please try again.
        </p>
      )}
      <div>
        <h1 className="text-3xl font-bold">Installed Packs</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          View and manage content packs installed in this organization.
        </p>
      </div>

      {isLoading && (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Loading...
        </p>
      )}

      {!isLoading && installations.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
          No packs installed yet.
        </div>
      )}

      {installations.length > 0 && (
        <div className="overflow-hidden rounded-lg border">
          <table className="w-full text-sm">
            <thead className="bg-[hsl(var(--secondary))]">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Pack</th>
                <th className="px-4 py-3 text-left font-medium">Version</th>
                <th className="px-4 py-3 text-left font-medium">Status</th>
                <th className="px-4 py-3 text-left font-medium">Installed</th>
              </tr>
            </thead>
            <tbody>
              {installations.map((install) => (
                <tr key={install.id} className="border-t">
                  <td className="px-4 py-3">
                    <Link
                      href={`/dashboard/orgs/${orgId}/installations/${install.id}`}
                      className="font-medium hover:text-[hsl(var(--primary))]"
                    >
                      {install.pack_id
                        ? install.pack_id.length > 12
                          ? `${install.pack_id.slice(0, 12)}...`
                          : install.pack_id
                        : "—"}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-[hsl(var(--muted-foreground))]">
                    {install.installed_version}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[install.status] ?? ""}`}
                    >
                      {install.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[hsl(var(--muted-foreground))]">
                    {new Date(install.installed_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data?.meta && installations.length < data.meta.total && (
        <p className="text-center text-sm text-[hsl(var(--muted-foreground))]">
          Showing {installations.length} of {data.meta.total} installations
        </p>
      )}
    </div>
  );
}
