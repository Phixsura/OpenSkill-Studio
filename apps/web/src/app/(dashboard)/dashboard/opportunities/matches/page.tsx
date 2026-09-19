"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";
import { cn } from "@/lib/utils";

interface MatchResult {
  opportunity_id: string;
  title: string;
  employer_name: string;
  opportunity_type: string;
  match_score: number;
  tier: string;
  reasons: { code: string; label: string; evidence: string }[];
  gaps: { code: string; label: string }[];
}

const TIER_STYLES: Record<string, string> = {
  great: "bg-green-100 text-green-700",
  good: "bg-blue-100 text-blue-700",
  fair: "bg-yellow-100 text-yellow-700",
};

export default function OpportunityMatchesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["opportunity-matches"],
    queryFn: () => apiWithAuth<{ data: MatchResult[] }>("/talent/opportunities/matches"),
  });

  const matches = data?.data ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Matched Opportunities</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Opportunities matched to your verified capabilities. Matches are explained — you can see
          exactly why each opportunity was recommended and where gaps exist.
        </p>
      </div>

      {isLoading && (
        <div className="text-[hsl(var(--muted-foreground))]">Finding your matches…</div>
      )}

      {!isLoading && matches.length === 0 && (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-8 text-center">
          <div className="mb-4 text-4xl">🔍</div>
          <h2 className="text-lg font-semibold">No Matches Yet</h2>
          <p className="mt-2 text-[hsl(var(--muted-foreground))]">
            Build your capability profile by completing skills, projects, and assessments. Make sure
            your passport is set to discoverable to see matches.
          </p>
          <Link
            href="/dashboard/passport"
            className="mt-4 inline-block rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))]"
          >
            Set Up Passport
          </Link>
        </div>
      )}

      <div className="space-y-4">
        {matches.map((match) => (
          <div
            key={match.opportunity_id}
            className="rounded-lg border bg-[hsl(var(--card))] p-6 shadow-sm"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <h3 className="text-lg font-semibold">{match.title}</h3>
                  <span
                    className={cn(
                      "rounded-full px-2.5 py-0.5 text-xs font-medium",
                      TIER_STYLES[match.tier] ?? "bg-gray-100 text-gray-600",
                    )}
                  >
                    {match.tier}
                  </span>
                </div>
                <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                  {match.employer_name} · {match.opportunity_type.replace(/_/g, " ")}
                </p>
              </div>
              <div className="ml-4 text-right">
                <div className="text-2xl font-bold">{Math.round(match.match_score * 100)}%</div>
                <div className="text-xs text-[hsl(var(--muted-foreground))]">match</div>
              </div>
            </div>

            {/* Reasons (strengths) */}
            {match.reasons.length > 0 && (
              <div className="mt-4">
                <p className="mb-2 text-sm font-medium text-green-700">Strong matches</p>
                <div className="flex flex-wrap gap-2">
                  {match.reasons.map((r, i) => (
                    <span
                      key={i}
                      className="inline-flex items-center rounded-full bg-green-50 px-3 py-1 text-xs text-green-700"
                    >
                      ✓ {r.label}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Gaps */}
            {match.gaps.length > 0 && (
              <div className="mt-3">
                <p className="mb-2 text-sm font-medium text-amber-700">Gaps</p>
                <div className="flex flex-wrap gap-2">
                  {match.gaps.map((g, i) => (
                    <span
                      key={i}
                      className="inline-flex items-center rounded-full bg-amber-50 px-3 py-1 text-xs text-amber-700"
                    >
                      △ {g.label}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-4 flex gap-3">
              <Link
                href={`/dashboard/opportunities/${match.opportunity_id}`}
                className="rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))]"
              >
                View & Apply
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
