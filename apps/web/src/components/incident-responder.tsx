"use client";

interface Incident { title: string; severity: string; status: string;
  affected: string[]; responders: string[]; }
interface IncidentResponderProps { incidents: Incident[]; open: number;
  resolved: number; bySeverity: Record<string, number>; }

const SEV_COLORS: Record<string, string> = {
  critical: "bg-red-500 text-white", major: "bg-orange-500 text-white",
  minor: "bg-yellow-400 text-black",
};

export function IncidentResponder({ incidents, open, resolved, bySeverity }: IncidentResponderProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚨 Incident Response</h3>
        <div className="flex gap-2 text-xs">
          {open > 0 && <span className="text-red-500">{open} open</span>}
          <span className="text-green-600">{resolved} resolved</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {incidents.map((inc, i) => (
          <div key={i} className="px-4 py-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className={`px-1.5 py-0.5 text-[10px] rounded ${SEV_COLORS[inc.severity] ?? ""}`}>{inc.severity}</span>
                <span className="text-sm font-medium">{inc.title}</span>
              </div>
              <span className="text-xs text-gray-400 capitalize">{inc.status}</span>
            </div>
            <div className="text-[10px] text-gray-400 mt-0.5">
              {inc.affected.join(", ")} · {inc.responders.length} responders
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
