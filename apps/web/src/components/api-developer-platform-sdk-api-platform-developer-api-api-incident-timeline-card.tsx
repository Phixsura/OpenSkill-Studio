"use client";

interface TimelineEntry { phase: string; message: string; author: string; }
interface IncidentInfo { incident_id: string; title: string; severity: string; current_phase: string; timeline: TimelineEntry[]; duration_minutes: number; }
interface Props { incidents: IncidentInfo[]; activeCount: number; appName: string; }

const sevEmoji: Record<string, string> = { minor: "🟡", major: "🟠", critical: "🔴" };
const phaseIcon: Record<string, string> = { detected: "🔍", investigating: "🔬", identified: "🎯", monitoring: "👁️", resolved: "✅" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiIncidentTimelineCard({ incidents, activeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚨 Incidents</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {activeCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">{activeCount} active</span>}
      </div>
      {incidents.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No incidents</p>
      ) : (
        <div className="space-y-2">
          {incidents.map((i) => (
            <div key={i.incident_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{sevEmoji[i.severity] ?? ""} {i.title}</span>
                <span className="text-gray-400">{phaseIcon[i.current_phase] ?? ""} {i.current_phase}</span>
              </div>
              {i.current_phase === "resolved" && <div className="text-[10px] text-gray-400">Resolved in {i.duration_minutes}m</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
