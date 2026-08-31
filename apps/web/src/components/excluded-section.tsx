"use client";

// Hard-constraint failures are ALWAYS separated from the ranked list and
// always counted, even when collapsed (ADR-012 R20).

export interface ExcludedFailure {
  code: string;
  detail?: string;
  capability?: string;
}

export interface ExcludedEntity {
  entity_id: string;
  name?: string | null;
  failures: ExcludedFailure[];
}

export function ExcludedSection({ excluded }: { excluded: ExcludedEntity[] }) {
  if (excluded.length === 0) return null;
  return (
    <details className="rounded-lg border border-dashed p-4">
      <summary className="cursor-pointer text-sm font-medium text-[hsl(var(--muted-foreground))]">
        Not eligible ({excluded.length})
      </summary>
      <ul className="mt-3 space-y-2">
        {excluded.map((entity) => (
          <li key={entity.entity_id} className="text-sm">
            <span className="font-medium">{entity.name ?? entity.entity_id}</span>
            <ul className="mt-0.5 list-inside list-disc text-xs text-[hsl(var(--muted-foreground))]">
              {entity.failures.map((f, i) => (
                <li key={i}>{f.detail ?? f.code}</li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </details>
  );
}
