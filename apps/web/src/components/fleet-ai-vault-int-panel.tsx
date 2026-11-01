"use client";
export function FleetAiVaultIntPanel({ vaults, active, secrets, accesses, rotations }: { vaults: number; active: number; secrets: number; accesses: number; rotations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 AI Vault</h3>
    <div className="text-sm">{active}/{vaults} active · {secrets} secrets · {accesses.toLocaleString()} accesses · {rotations} rotations</div>
  </div>);
}
