"use client";

interface InviteCode { code: string; maxUses: number; uses: number; active: boolean; }
interface InviteCodeManagerProps { codes: InviteCode[]; totalRedemptions: number;
  activeCount: number; onCreate: () => void; }

export function InviteCodeManager({ codes, totalRedemptions, activeCount, onCreate }: InviteCodeManagerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎟️ Invite Codes</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{activeCount} active · {totalRedemptions} redeemed</span>
          <button onClick={onCreate} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ Create</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {codes.map(c => (
          <div key={c.code} className={`flex items-center justify-between px-4 py-2.5 ${!c.active ? "opacity-50" : ""}`}>
            <div className="flex items-center gap-2">
              <span className="text-sm font-mono font-bold tracking-wider">{c.code}</span>
              <span className={`text-[10px] ${c.active ? "text-green-600" : "text-gray-400"}`}>
                {c.active ? "● Active" : "○ Exhausted"}
              </span>
            </div>
            <span className="text-xs text-gray-400">{c.uses}/{c.maxUses} used</span>
          </div>
        ))}
      </div>
    </div>
  );
}
