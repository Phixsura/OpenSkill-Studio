"use client";
interface Silence { name: string; matcher: string; durationMinutes: number; reason: string; }
interface AlertSilencePanelProps { silences: Silence[]; activeCount: number; }
export function AlertSilencePanel({ silences, activeCount }: AlertSilencePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔇 Alert Silences</h3>
        <span className="text-xs text-gray-400">{activeCount} active</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {silences.map(s => (
          <div key={s.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{s.matcher}</span>
            <span className="text-gray-400">{s.durationMinutes}min — {s.reason}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
