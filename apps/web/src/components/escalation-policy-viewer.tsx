"use client";

interface EscLevel { level: number; contacts: string[]; channel: string; waitMin: number; }
interface EscalationPolicyViewerProps { name: string; levels: EscLevel[];
  timeline: { level: number; atMin: number; contacts: string[] }[]; }

const CH_ICONS: Record<string, string> = { email: "📧", pager: "📟", phone: "📞", slack: "💬" };

export function EscalationPolicyViewer({ name, levels, timeline }: EscalationPolicyViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚨 {name}</h3>
        <span className="text-xs text-gray-400">{levels.length} levels</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {levels.map(lv => (
          <div key={lv.level} className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-3">
              <span className="w-6 h-6 rounded-full bg-red-100 dark:bg-red-900/20 text-red-600 flex items-center justify-center text-xs font-bold">{lv.level}</span>
              <div>
                <div className="text-sm">{lv.contacts.join(", ")}</div>
                <div className="text-[10px] text-gray-400">{CH_ICONS[lv.channel] ?? "📨"} {lv.channel} · wait {lv.waitMin}min</div>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="p-3 border-t dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
        <div className="text-[10px] text-gray-400">Timeline: {timeline.map(t => `L${t.level} @${t.atMin}min`).join(" → ")}</div>
      </div>
    </div>
  );
}
