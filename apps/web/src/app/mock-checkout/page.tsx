"use client";

import { Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

// R113[M21]: the mock billing provider redirects checkouts to
// ${frontend_url}/mock-checkout?session=...&kind=... but no such route
// existed — every dev/E2E checkout landed on a 404. Mock webhooks are
// HMAC-signed with a server-derived key (mock_webhook_key), so the frontend
// CANNOT forge a completion event — this page only surfaces the session ref
// and points at the real completion mechanisms.
function MockCheckoutInner() {
  const searchParams = useSearchParams();
  const session = searchParams.get("session");
  const kind = searchParams.get("kind");

  return (
    <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--background))] p-4">
      <div className="w-full max-w-md space-y-4 rounded-lg border p-6">
        <h1 className="text-lg font-semibold">Mock checkout — dev only</h1>
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          This is the mock billing provider&apos;s checkout page. No payment is collected here —
          complete the session via the signed mock webhook endpoint or the E2E test driver.
        </p>
        {kind && (
          <p className="text-sm">
            <span className="text-[hsl(var(--muted-foreground))]">Kind:</span>{" "}
            <span className="font-mono text-xs">{kind}</span>
          </p>
        )}
        <div className="rounded-md bg-[hsl(var(--secondary))] px-4 py-2">
          <p className="text-xs text-[hsl(var(--muted-foreground))]">Session reference</p>
          <p className="break-all font-mono text-sm">{session ?? "(missing)"}</p>
        </div>
        <Link
          href="/dashboard"
          className="inline-block text-sm text-[hsl(var(--primary))] underline-offset-2 hover:underline"
        >
          ← Back to billing
        </Link>
      </div>
    </div>
  );
}

export default function MockCheckoutPage() {
  // useSearchParams requires a Suspense boundary in the App Router
  return (
    <Suspense
      fallback={<p className="p-8 text-sm text-[hsl(var(--muted-foreground))]">Loading…</p>}
    >
      <MockCheckoutInner />
    </Suspense>
  );
}
