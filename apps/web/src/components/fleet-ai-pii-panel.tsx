"use client";
export function FleetAiPiiPanel({ services, active, docs, piiFound, redacted }: { services: number; active: number; docs: number; piiFound: number; redacted: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 AI PII Redaction</h3>
    <div className="text-sm">{active}/{services} active · {docs.toLocaleString()} docs · {piiFound.toLocaleString()} PII · {redacted.toLocaleString()} redacted</div>
  </div>);
}
