"use client";
export function FleetKarpenterPanel({ provisioners, active, launched, terminated, savings }: { provisioners: number; active: number; launched: number; terminated: number; savings: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 Karpenter</h3>
    <div className="text-sm">{active}/{provisioners} active · ↑{launched} ↓{terminated} nodes/24h · ${savings} saved</div>
  </div>);
}
