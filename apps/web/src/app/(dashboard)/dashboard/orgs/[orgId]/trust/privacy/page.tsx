"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface PrivacyReview {
  id: string;
  system_id: string;
  title: string;
  status: string;
  data_classification: string;
  legal_basis: string | null;
  regions: string[];
  created_at: string;
}

interface ConsentRecord {
  id: string;
  system_id: string;
  purpose: string;
  consent_status: string;
  data_categories: string[];
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  in_review: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  requires_changes: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  granted: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  denied: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  withdrawn: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  not_required: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
};

const CLASS_COLORS: Record<string, string> = {
  public: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  internal: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  confidential: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  sensitive_pii: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  highly_sensitive: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

function Badge({ label, colors }: { label: string; colors: string }) {
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${colors}`}>
      {label.replace(/_/g, " ")}
    </span>
  );
}

export default function PrivacyPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();
  const tab = (searchParams.get("tab") as "reviews" | "consent") || "reviews";
  const base = `/dashboard/orgs/${orgId}/trust/privacy`;

  const { data: reviewData, isLoading: rLoading } = useQuery({
    queryKey: ["trust-privacy-reviews", orgId],
    queryFn: () => apiWithAuth<{ data: PrivacyReview[]; meta: { total: number } }>(`/orgs/${orgId}/trust/privacy-reviews?per_page=50`),
    enabled: tab === "reviews",
  });

  const { data: consentData, isLoading: cLoading } = useQuery({
    queryKey: ["trust-consent-records", orgId],
    queryFn: () => apiWithAuth<{ data: ConsentRecord[]; meta: { total: number } }>(`/orgs/${orgId}/trust/consent-records?per_page=50`),
    enabled: tab === "consent",
  });

  const reviews = reviewData?.data ?? [];
  const consents = consentData?.data ?? [];
  const isLoading = tab === "reviews" ? rLoading : cLoading;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Privacy & Consent</h1>

      <div className="flex gap-1 border-b">
        {(["reviews", "consent"] as const).map((t) => (
          <button
            key={t}
            onClick={() => router.push(`${base}?tab=${t}`)}
            className={`px-4 py-2 text-sm font-medium border-b-2 ${
              tab === t
                ? "border-[hsl(var(--primary))] text-[hsl(var(--primary))]"
                : "border-transparent text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
            }`}
          >
            {t === "reviews" ? "Privacy Reviews" : "Consent Records"}
          </button>
        ))}
      </div>

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}

      {tab === "reviews" && !isLoading && (
        reviews.length === 0 ? (
          <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">No privacy reviews.</div>
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Title</th>
                  <th className="px-4 py-2 font-medium">Classification</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium">Legal Basis</th>
                  <th className="px-4 py-2 font-medium">Regions</th>
                  <th className="px-4 py-2 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                {reviews.map((r) => (
                  <tr key={r.id} className="border-b last:border-0 hover:bg-[hsl(var(--secondary))]">
                    <td className="px-4 py-2 font-medium">{r.title}</td>
                    <td className="px-4 py-2"><Badge label={r.data_classification} colors={CLASS_COLORS[r.data_classification] || ""} /></td>
                    <td className="px-4 py-2"><Badge label={r.status} colors={STATUS_COLORS[r.status] || ""} /></td>
                    <td className="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]">{r.legal_basis?.replace(/_/g, " ") || "—"}</td>
                    <td className="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]">{r.regions.join(", ") || "—"}</td>
                    <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">{new Date(r.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      {tab === "consent" && !isLoading && (
        consents.length === 0 ? (
          <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">No consent records.</div>
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
              <thead className="border-b bg-[hsl(var(--secondary))] text-left">
                <tr>
                  <th className="px-4 py-2 font-medium">Purpose</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium">Categories</th>
                  <th className="px-4 py-2 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                {consents.map((c) => (
                  <tr key={c.id} className="border-b last:border-0 hover:bg-[hsl(var(--secondary))]">
                    <td className="px-4 py-2 font-medium">{c.purpose}</td>
                    <td className="px-4 py-2"><Badge label={c.consent_status} colors={STATUS_COLORS[c.consent_status] || ""} /></td>
                    <td className="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]">{c.data_categories.join(", ") || "—"}</td>
                    <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">{new Date(c.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}
    </div>
  );
}
