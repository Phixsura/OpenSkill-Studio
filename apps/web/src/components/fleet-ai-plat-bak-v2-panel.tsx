"use client";
export function FleetAiPlatBakV2Panel({ systems, active, backups, sizeTb, rpo, verified }: { systems: number; active: number; backups: number; sizeTb: number; rpo: number; verified: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 AI Backup v2</h3>
    <div className="text-sm">{active}/{systems} active · {backups} backups · {sizeTb}TB · RPO {rpo}m · {verified ? "✅" : "⚠️"}</div>
  </div>);
}
