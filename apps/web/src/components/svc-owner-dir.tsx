"use client";

interface OwnerInfo { service: string; team: string; oncall: string; escalation: string[]; }
interface SvcOwnerDirProps { services: OwnerInfo[]; teamCount: number; }

export function SvcOwnerDir({ services, teamCount }: SvcOwnerDirProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">👥 Service Owners</h3>
        <span className="text-xs text-gray-400">{services.length} services · {teamCount} teams</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="px-4 py-2 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-semibold">{s.service}</span>
              <span className="text-gray-400">{s.team}</span>
            </div>
            <div className="text-gray-400">on-call: <span className="text-blue-500">{s.oncall}</span> · escalation: {s.escalation.join(" → ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
