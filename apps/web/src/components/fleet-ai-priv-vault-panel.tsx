"use client";
export function FleetAiPrivVaultPanel({ vaults, active, pii, redacted, tokenized }: { vaults: number; active: number; pii: number; redacted: number; tokenized: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 AI Privacy Vault</h3>
    <div className="text-sm">{active}/{vaults} active · {pii.toLocaleString()} PII · {redacted.toLocaleString()} redacted · {tokenized.toLocaleString()} tokenized</div>
  </div>);
}
