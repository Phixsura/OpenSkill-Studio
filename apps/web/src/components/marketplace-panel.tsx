"use client";

import { useEffect, useState } from "react";
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

interface PurchaseResult {
  data: { id: string; status: string; checkout_url?: string };
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
  // R101[H13]: checkout was unreachable — payment_method was hardcoded
  // "credit". Zero-credit tenants can now pay via the hosted checkout.
  const [payMethod, setPayMethod] = useState<"credit" | "checkout">("credit");
  // R101[H0]: per-attempt key — the old stable `${orgId}:${listingId}` key
  // resumed a REFUNDED purchase as a false success forever. Regenerated per
  // confirm-flow open; network retries within one attempt still dedupe.
  const [attemptKey, setAttemptKey] = useState("");

  const orgsQuery = useQuery({
    queryKey: ["my-orgs"],
    queryFn: () => apiWithAuth<{ data: OrgSummary[] }>("/orgs"),
    enabled: isAuthed,
  });
  const allOrgs = orgsQuery.data?.data ?? [];
  const adminOrgs = allOrgs.filter((o) => o.role === "owner" || o.role === "admin");
  // R101[M8]: license status is member-readable — a plain member of the only
  // org saw "Sign in..." and never the Licensed badge. Read with any org;
  // purchase still requires an admin org.
  const statusOrgId = selectedOrg || adminOrgs[0]?.id || allOrgs[0]?.id || null;
  const purchaseOrgId = selectedOrg || adminOrgs[0]?.id || null;
  const canPurchase = adminOrgs.length > 0;

  // R101[M7]: the public badge endpoint deliberately hides partner_only
  // listings — signed-in org members query the org-scoped view, which
  // includes them when the tenant is partner-attributed.
  const listingQuery = useQuery({
    queryKey: ["registry-listing", productType, productId, statusOrgId ?? "anon"],
    queryFn: () =>
      statusOrgId
        ? apiWithAuth<{ data: Record<string, Listing> }>(
            `/orgs/${statusOrgId}/marketplace/listings-view?product_type=${productType}&product_ids=${productId}`,
          )
        : api<{ data: Record<string, Listing> }>(
            `/registry/listings?product_type=${productType}&product_ids=${productId}`,
          ),
  });
  const currentListing = listingQuery.data?.data?.[productId] ?? null;
  // R113[L9]: switching the org selector to an org whose tenant is not
  // partner-attributed excludes a partner_only listing from that org's
  // listings-view — listing went null and the ENTIRE panel (org selector
  // included) unmounted mid-interaction, stranding the user with no way to
  // switch back. Keep the last non-null listing and render an explicit
  // "not available" state with the selector instead of vanishing.
  const [lastListing, setLastListing] = useState<Listing | null>(null);
  useEffect(() => {
    if (currentListing) setLastListing(currentListing);
  }, [currentListing]);
  const listing = currentListing ?? lastListing;
  const listingUnavailable =
    currentListing == null && lastListing != null && listingQuery.isSuccess;

  const licenseQuery = useQuery({
    queryKey: ["license-status", statusOrgId, productType, productId],
    queryFn: () =>
      apiWithAuth<{ data: LicenseStatus }>(
        `/orgs/${statusOrgId}/marketplace/license-status?product_type=${productType}&product_ids=${productId}`,
      ),
    enabled: isAuthed && statusOrgId != null && listing != null,
  });
  const licensed = licenseQuery.data?.data?.[productId]?.licensed ?? false;

  const purchaseMutation = useMutation({
    mutationFn: () =>
      apiWithAuth<PurchaseResult>(`/orgs/${purchaseOrgId}/marketplace/purchases`, {
        method: "POST",
        body: JSON.stringify({
          listing_id: listing!.id,
          payment_method: payMethod,
          idempotency_key: attemptKey,
        }),
      }),
    onSuccess: (res) => {
      // R101[H13]: checkout hands back a hosted session URL — follow it
      if (res?.data?.checkout_url) {
        window.location.href = res.data.checkout_url;
        return;
      }
      // R101[H0]: trust the returned STATUS — an idempotent resume can hand
      // back a pending/other-state purchase; only "paid" means licensed now.
      if (res?.data?.status === "paid") {
        toast.success("Purchased — the pack is now licensed for your organization");
      } else {
        toast.info(`Purchase ${res?.data?.status ?? "recorded"} — check the tenant Licenses page`);
      }
      setPurchasing(false);
      queryClient.invalidateQueries({ queryKey: ["license-status"] });
      // R101[L13]: the tenant Licenses/purchases pages render this too
      queryClient.invalidateQueries({ queryKey: ["tenant-licenses"] });
      queryClient.invalidateQueries({ queryKey: ["tenant-purchases"] });
    },
    onError: (e) => {
      setPurchasing(false);
      if (e instanceof ApiError) {
        if (e.code === "INSUFFICIENT_CREDIT") {
          toast.error("Not enough credit — ask your tenant admin to top up the credit balance.");
          return;
        }
        if (e.code === "ALREADY_LICENSED") {
          toast.info("Already licensed.");
          queryClient.invalidateQueries({ queryKey: ["license-status"] });
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

  // R101[H1]: included_with_plan is not purchasable — the old panel showed a
  // bogus "Paid" price and a Purchase button that always 409'd.
  if (listing.offer_type === "included_with_plan") {
    return (
      <div className="rounded-lg border p-4">
        <p className="text-sm">
          <span className="font-semibold">Included with plan</span>
          <span className="ml-2 text-xs text-[hsl(var(--muted-foreground))]">
            Available on qualifying subscription plans — install directly.
          </span>
        </p>
      </div>
    );
  }
  // private listings are seller-internal; no public purchase surface
  if (listing.offer_type === "private") return null;

  // R113[L9]: the selected org's listings-view excludes this listing (e.g. a
  // non-partner org on a partner_only listing) — say so instead of vanishing.
  if (listingUnavailable) {
    return (
      <div className="rounded-lg border p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Not available for this organization.
          </p>
          {adminOrgs.length > 1 && (
            <select
              className="rounded-md border bg-transparent px-2 py-1.5 text-sm"
              value={statusOrgId ?? ""}
              onChange={(e) => setSelectedOrg(e.target.value)}
            >
              {adminOrgs.map((o) => (
                <option key={o.id} value={o.id}>
                  {o.name}
                </option>
              ))}
            </select>
          )}
        </div>
      </div>
    );
  }

  const startPurchase = () => {
    // fresh key per confirm-flow open (H0)
    setAttemptKey(
      `${purchaseOrgId}:${listing.id}:${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`,
    );
    setPurchasing(true);
  };

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
              {listing.offer_type === "partner_only" ? " · partner tenants only" : ""}
            </span>
          </p>
          {listing.seller_org_name && (
            <p className="text-xs text-[hsl(var(--muted-foreground))]">
              Sold by {listing.seller_org_name}
            </p>
          )}
        </div>
        {licensed ? (
          <div className="flex items-center gap-2">
            {/* R101[H2]: multi-org admins must still be able to switch to an
                unlicensed org and purchase for it — the badge previously hid
                the selector permanently once the default org was licensed. */}
            {adminOrgs.length > 1 && (
              <select
                className="rounded-md border bg-transparent px-2 py-1.5 text-sm"
                value={statusOrgId ?? ""}
                onChange={(e) => setSelectedOrg(e.target.value)}
              >
                {adminOrgs.map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.name}
                  </option>
                ))}
              </select>
            )}
            <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
              ✓ Licensed
            </span>
          </div>
        ) : isAuthed && canPurchase ? (
          purchasing ? (
            <div className="flex flex-wrap items-center gap-2">
              {adminOrgs.length > 1 && (
                <select
                  className="rounded-md border bg-transparent px-2 py-1.5 text-sm"
                  value={purchaseOrgId ?? ""}
                  onChange={(e) => setSelectedOrg(e.target.value)}
                >
                  {adminOrgs.map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.name}
                    </option>
                  ))}
                </select>
              )}
              <span className="text-sm">
                {/* R101[L4]: show the charged amount at the confirm step */}
                Pay{" "}
                {listing.price_minor != null && listing.currency
                  ? formatMinor(listing.price_minor, listing.currency)
                  : ""}{" "}
                with
              </span>
              <select
                className="rounded-md border bg-transparent px-2 py-1.5 text-sm"
                value={payMethod}
                onChange={(e) => setPayMethod(e.target.value as "credit" | "checkout")}
              >
                <option value="credit">credit balance</option>
                <option value="checkout">card checkout</option>
              </select>
              <span className="text-xs text-[hsl(var(--muted-foreground))]">
                (converted to your tenant currency at purchase)
              </span>
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
            <Button onClick={startPurchase}>Purchase license</Button>
          )
        ) : isAuthed ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Ask an organization admin to purchase this license.
          </p>
        ) : (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Sign in with an org admin account to purchase.
          </p>
        )}
      </div>
    </div>
  );
}
