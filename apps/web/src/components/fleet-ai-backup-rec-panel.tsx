"use client";
export function FleetAiBackupRecPanel({ systems, active, backups, sizeTb, rpo, rto }: { systems: number; active: number; backups: number; sizeTb: number; rpo: number; rto: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 AI Backup & Recovery</h3>
    <div className="text-sm">{active}/{systems} active · {backups} backups · {sizeTb}TB · RPO {rpo}m · RTO {rto}m</div>
  </div>);
}
