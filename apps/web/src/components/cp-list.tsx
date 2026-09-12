"use client";

import { Button } from "@/components/ui/button";

/** R101: shared pager — ~10 commercial list pages ignored pagination meta and
 * silently truncated at the backend default page size with no pager. */
export function Pager({
  page,
  hasMore,
  onPage,
}: {
  page: number;
  hasMore: boolean;
  onPage: (p: number) => void;
}) {
  if (page === 1 && !hasMore) return null;
  return (
    <div className="flex items-center gap-2 pt-2">
      <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => onPage(page - 1)}>
        Prev
      </Button>
      <span className="text-xs text-[hsl(var(--muted-foreground))]">Page {page}</span>
      <Button variant="outline" size="sm" disabled={!hasMore} onClick={() => onPage(page + 1)}>
        Next
      </Button>
    </div>
  );
}

/** R101: shared query-error banner — list pages rendered errors as
 * authoritative empty states ("No invoices yet.") with no retry hint. */
export function QueryError({ error, what }: { error: unknown; what: string }) {
  const message =
    error && typeof error === "object" && "message" in error
      ? String((error as { message: unknown }).message)
      : "Request failed";
  return (
    <p className="rounded-md border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-900 dark:border-red-800 dark:bg-red-950 dark:text-red-100">
      Could not load {what}: {message}
    </p>
  );
}
