"use client";
export function FleetAiPrivacyV8Panel({ systems, active, pii, redacted, gdpr, ccpa }: { systems: number; active: number; pii: number; redacted: number; gdpr: boolean; ccpa: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 AI Privacy v8</h3>
    <div className="text-sm">{active}/{systems} active · {pii.toLocaleString()} PII · {redacted.toLocaleString()} redacted · {gdpr ? "✅ GDPR" : "⚠️"} · {ccpa ? "✅ CCPA" : "⚠️"}</div>
  </div>);
}
