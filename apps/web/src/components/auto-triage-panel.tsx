"use client";

interface TriageResult { incidentType: string; assignedTeam: string; severity: string; escalate: boolean; }
interface AutoTriagePanelProps { triages: TriageResult[]; total: number;
  byTeam: Record<string, number>; bySeverity: Record<string, number>; }

const SEV_COLORS: Record<string, string> = {
  critical: "bg-red-500 text-white", high: "bg-orange-500 text-white",
  medium: "bg-yellow-400", low: "bg-blue-400 text-white",
};

export function AutoTriagePanel({ triages, total, byTeam, bySeverity }: AutoTriagePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🤖 Auto-Triage</h3>
        <span className="text-xs text-gray-400">{total} triaged</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {triages.map((t, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex gap-2">
              <span className={`px-1.5 py-0.5 rounded text-[10px] ${SEV_COLORS[t.severity] ?? ""}`}>{t.severity}</span>
              <span>{t.incidentType}</span>
              {t.escalate && <span className="text-red-500">📟</span>}
            </div>
            <span className="text-gray-400">→ {t.assignedTeam}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
