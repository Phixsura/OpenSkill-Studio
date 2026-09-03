"use client";

import { useState } from "react";
import Link from "next/link";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { apiWithAuth, ApiError } from "@/lib/api";

interface OrgSummary {
  id: string;
  name: string;
  role: string | null;
}

// Roles allowed to install (mirror of backend INSTRUCTOR_ROLES / WRITE_ROLES)
const INSTALL_ROLES = new Set(["owner", "admin", "instructor"]);

/** R101[H3]: the registry "Install in your organization →" CTA linked to
 * /dashboard — no UI could ever call the install endpoints. This drives the
 * real POST /orgs/{orgId}/installations | workflow-installations. */
export function InstallButton({
  productType,
  packId,
  packName,
  isAuthed,
}: {
  productType: "skill_pack" | "workflow_pack";
  packId: string;
  packName: string;
  isAuthed: boolean;
}) {
  const [selecting, setSelecting] = useState(false);
  const [selectedOrg, setSelectedOrg] = useState("");
  const [installedOrg, setInstalledOrg] = useState<string | null>(null);

  const orgsQuery = useQuery({
    queryKey: ["my-orgs"],
    queryFn: () => apiWithAuth<{ data: OrgSummary[] }>("/orgs"),
    enabled: isAuthed,
  });
  const installOrgs = (orgsQuery.data?.data ?? []).filter(
    (o) => o.role != null && INSTALL_ROLES.has(o.role),
  );
  const orgId = selectedOrg || installOrgs[0]?.id || null;

  const endpoint =
    productType === "workflow_pack"
      ? `/orgs/${orgId}/workflow-installations`
      : `/orgs/${orgId}/installations`;

  const installMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(endpoint, {
        method: "POST",
        body: JSON.stringify({ pack_id: packId }),
      }),
    onSuccess: () => {
      toast.success(`Installed ${packName} — available in your organization now`);
      setInstalledOrg(orgId);
      setSelecting(false);
    },
    onError: (e) => {
      setSelecting(false);
      if (e instanceof ApiError) {
        if (e.code === "LICENSE_REQUIRED") {
          // R113[L8]: the install org can differ from the org whose license
          // badge is shown above — name the mismatch instead of confusing.
          toast.error(
            "A license is required for the selected organization — check which org holds the license above, or purchase for this org first.",
          );
          return;
        }
        if (e.code === "ALREADY_INSTALLED") {
          toast.info("Already installed in this organization.");
          setInstalledOrg(orgId);
          return;
        }
        toast.error(e.message);
      } else {
        toast.error("Install failed");
      }
    },
  });

  if (!isAuthed) {
    return (
      <Link href="/login">
        <Button className="mt-4" aria-label={`Install ${packName}`}>
          Sign in to install →
        </Button>
      </Link>
    );
  }
  if (installOrgs.length === 0) {
    return (
      <p className="mt-4 text-sm text-[hsl(var(--muted-foreground))]">
        Installing requires an instructor or admin role in an organization.
      </p>
    );
  }
  if (installedOrg) {
    return (
      <span className="mt-4 inline-block rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
        ✓ Installed
      </span>
    );
  }
  if (selecting) {
    return (
      <div className="mt-4 flex flex-wrap items-center gap-2">
        {installOrgs.length > 1 && (
          <select
            className="rounded-md border bg-transparent px-2 py-1.5 text-sm"
            value={orgId ?? ""}
            onChange={(e) => setSelectedOrg(e.target.value)}
          >
            {installOrgs.map((o) => (
              <option key={o.id} value={o.id}>
                {o.name}
              </option>
            ))}
          </select>
        )}
        <Button
          size="sm"
          onClick={() => installMutation.mutate()}
          disabled={installMutation.isPending}
        >
          {installMutation.isPending ? "Installing…" : "Confirm install"}
        </Button>
        <Button size="sm" variant="outline" onClick={() => setSelecting(false)}>
          Cancel
        </Button>
      </div>
    );
  }
  return (
    <Button className="mt-4" onClick={() => setSelecting(true)} aria-label={`Install ${packName}`}>
      Install in your organization →
    </Button>
  );
}
