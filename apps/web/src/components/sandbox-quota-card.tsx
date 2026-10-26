"use client";

interface SandboxQuota {
  tier: string; activeSandboxes: number; maxSandboxes: number;
  memoryUsedMb: number; maxMemoryMb: number;
}

const tierColors: Record<string, string> = {
  free: "bg-gray-100 text-gray-700", pro: "bg-blue-100 text-blue-700", enterprise: "bg-purple-100 text-purple-700",
};

export function SandboxQuotaCard({ quota, onUpgrade }: { quota: SandboxQuota; onUpgrade?: () => void }) {
  const sandboxPct = Math.round(quota.activeSandboxes / quota.maxSandboxes * 100);
  const memPct = Math.round(quota.memoryUsedMb / quota.maxMemoryMb * 100);
  return (
    <div className="border dark:border-gray-700 rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span className="font-bold text-sm">Sandbox Resources</span>
        <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${tierColors[quota.tier] || tierColors.free}`}>{quota.tier}</span>
      </div>
      <div className="space-y-2">
        <div>
          <div className="flex justify-between text-xs mb-1"><span>Sandboxes</span><span>{quota.activeSandboxes}/{quota.maxSandboxes}</span></div>
          <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full"><div className={`h-full rounded-full ${sandboxPct >= 90 ? "bg-red-500" : "bg-blue-500"}`} style={{ width: `${sandboxPct}%` }} /></div>
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1"><span>Memory</span><span>{quota.memoryUsedMb}MB/{quota.maxMemoryMb}MB</span></div>
          <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full"><div className={`h-full rounded-full ${memPct >= 90 ? "bg-red-500" : "bg-green-500"}`} style={{ width: `${memPct}%` }} /></div>
        </div>
      </div>
      {quota.tier !== "enterprise" && <button onClick={onUpgrade} className="w-full text-xs bg-blue-500 text-white rounded-lg py-1.5 hover:bg-blue-600">Upgrade Plan</button>}
    </div>
  );
}
