"use client";
export function FleetAiPrivacyV7Panel({ systems, active, pii, redacted, gdpr }: { systems: number; active: number; pii: number; redacted: number; gdpr: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 AI Privacy v7</h3>
    <div className="text-sm">{active}/{systems} active · {pii.toLocaleString()} PII · {redacted.toLocaleString()} redacted · {gdpr ? "✅ GDPR" : "⚠️"}</div>
  </div>);
}
