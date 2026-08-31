"use client";

// Explainable recommendation card (ADR-012 D9/R20):
// tier label instead of raw score (score only in tooltip), reason chips,
// gap warnings with optional remediation link.

import Link from "next/link";

export interface MatchReason {
  code: string;
  label: string;
  evidence?: string;
}

export interface MatchGap {
  code: string;
  label: string;
  remediation_entity_id?: string;
}

export interface MatchResultItem {
  entity_id: string;
  entity_type: string;
  name?: string | null;
  rank?: number | null;
  score?: number | null;
  tier?: string | null;
  reasons: MatchReason[];
  gaps: MatchGap[];
  explain?: Record<string, unknown> | null;
}

const TIER_STYLES: Record<string, { label: string; className: string }> = {
  great: {
    label: "Excellent match",
    className: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  },
  good: {
    label: "Good match",
    className: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  },
  fair: {
    label: "Fair match",
    className: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
  },
};

export function MatchResultCard({
  result,
  remediationHref,
  children,
}: {
  result: MatchResultItem;
  remediationHref?: (gap: MatchGap) => string | null;
  children?: React.ReactNode;
}) {
  const tier = result.tier ? TIER_STYLES[result.tier] : null;

  return (
    <div className="rounded-lg border p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            {result.rank != null && (
              <span className="text-sm text-[hsl(var(--muted-foreground))]">
                #{result.rank}
              </span>
            )}
            <h3 className="truncate font-semibold">{result.name ?? result.entity_id}</h3>
          </div>
          {tier && (
            <span
              className={`mt-1 inline-block rounded-full px-2 py-0.5 text-xs font-medium ${tier.className}`}
              title={
                result.score != null ? `Score: ${result.score.toFixed(4)}` : undefined
              }
            >
              {tier.label}
            </span>
          )}
        </div>
        {children && <div className="shrink-0">{children}</div>}
      </div>

      {result.reasons.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {result.reasons.slice(0, 3).map((reason) => (
            <span
              key={reason.code + reason.label}
              className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs"
              title={reason.evidence ? `Evidence: ${reason.evidence}` : undefined}
            >
              {reason.label}
            </span>
          ))}
        </div>
      )}

      {result.gaps.length > 0 && (
        <ul className="mt-3 space-y-1">
          {result.gaps.map((gap) => {
            const href = remediationHref?.(gap) ?? null;
            return (
              <li
                key={gap.code + gap.label}
                className="flex items-center gap-2 text-xs text-amber-700 dark:text-amber-400"
              >
                <span aria-hidden>⚠</span>
                <span>{gap.label}</span>
                {href && (
                  <Link href={href} className="underline">
                    Learn this
                  </Link>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
