"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { api, apiWithAuth, ApiError } from "@/lib/api";
import { formatMinor } from "@/lib/cp";

interface Listing {
  id: string;
  product_type: string;
  product_id: string;
  offer_type: string;
  price_minor: number | null;
  currency: string | null;
  license_scope: string;
  seat_limit: number | null;
  seller_org_name: string | null;
}

interface LicenseStatus {
  [productId: string]: { licensed: boolean; scope?: string; source?: string };
}

interface OrgSummary {
  id: string;
  name: string;
  role: string | null;
}

/** Price badge + purchase action for a registry pack detail page (#27 §26).
 * Renders nothing when the pack has no active paid listing. */
export function MarketplacePanel({
  productType,
  productId,
  isAuthed,
}: {
  productType: "skill_pack" | "workflow_pack";
  productId: string;
  isAuthed: boolean;
}) {
  const queryClient = useQueryClient();
  const [purchasing, setPurchasing] = useState(false);
  const [selectedOrg, setSelectedOrg] = useState("");

  const orgsQuery = useQuery({
    queryKey: ["my-orgs"],
    queryFn: () => apiWithAuth<{ data: OrgSummary[] }>("/orgs"),
    enabled: isAuthed,
  });
  const adminOrgs = (orgsQuery.data?.data ?? []).filter(
    (o) => o.role === "owner" || o.role === "admin",
  );
  const orgId = selectedOrg || adminOrgs[0]?.id || null;

  const listingQuery = useQuery({
    queryKey: ["registry-listing", productType, productId],
    queryFn: () =>
      api<{ data: Record<string, Listing> }>(
        `/registry/listings?product_type=${productType}&product_ids=${productId}`,
      ),
  });
  const listing = listingQuery.data?.data?.[productId] ?? null;

  const licenseQuery = useQuery({
    queryKey: ["license-status", orgId, productType, productId],
    queryFn: () =>
      apiWithAuth<{ data: LicenseStatus }>(
        `/orgs/${orgId}/marketplace/license-status?product_type=${productType}&product_ids=${productId}`,
      ),
    enabled: isAuthed && orgId != null && listing != null,
  });
  const licensed = licenseQuery.data?.data?.[productId]?.licensed ?? false;

  const purchaseMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/marketplace/purchases`, {
        method: "POST",
        body: JSON.stringify({
          listing_id: listing!.id,
          payment_method: "credit",
          idempotency_key: `${orgId}:${listing!.id}`,
        }),
      }),
    onSuccess: () => {
      toast.success("Purchased — the pack is now licensed for your organization");
      setPurchasing(false);
      queryClient.invalidateQueries({ queryKey: ["license-status", orgId] });
    },
    onError: (e) => {
      setPurchasing(false);
      if (e instanceof ApiError) {
        if (e.code === "INSUFFICIENT_CREDIT") {
          toast.error("Not enough credit — top up on the tenant Credits page first.");
          return;
        }
        if (e.code === "ALREADY_LICENSED") {
          toast.info("Already licensed.");
          queryClient.invalidateQueries({ queryKey: ["license-status", orgId] });
          return;
        }
        toast.error(e.message);
      } else {
        toast.error("Purchase failed");
      }
    },
  });

  if (!listing) return null;
  if (listing.offer_type === "free") return null;

  return (
    <div className="rounded-lg border p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-lg font-bold">
            {listing.price_minor != null && listing.currency
              ? formatMinor(listing.price_minor, listing.currency)
              : "Paid"}
            <span className="ml-2 text-xs font-normal text-[hsl(var(--muted-foreground))]">
              {listing.license_scope}
              {listing.seat_limit ? ` · ${listing.seat_limit} seats` : ""} license
            </span>
          </p>
          {listing.seller_org_name && (
            <p className="text-xs text-[hsl(var(--muted-foreground))]">
              Sold by {listing.seller_org_name}
            </p>
          )}
        </div>
        {licensed ? (
          <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
            ✓ Licensed
          </span>
        ) : isAuthed && orgId ? (
          purchasing ? (
            <div className="flex flex-wrap items-center gap-2">
              {adminOrgs.length > 1 && (
                <select
                  className="rounded-md border bg-transparent px-2 py-1.5 text-sm"
                  value={orgId}
                  onChange={(e) => setSelectedOrg(e.target.value)}
                >
                  {adminOrgs.map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.name}
                    </option>
                  ))}
                </select>
              )}
              <span className="text-sm">Pay with credit balance?</span>
              <Button
                size="sm"
                onClick={() => purchaseMutation.mutate()}
                disabled={purchaseMutation.isPending}
              >
                Confirm
              </Button>
              <Button size="sm" variant="outline" onClick={() => setPurchasing(false)}>
                Cancel
              </Button>
            </div>
          ) : (
            <Button onClick={() => setPurchasing(true)}>Purchase license</Button>
          )
        ) : (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Sign in with an org admin account to purchase.
          </p>
        )}
      </div>
    </div>
  );
}
