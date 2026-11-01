"use client";
interface ChangeRiskPanelProps { score: number; level: string; tags: string[]; changeDescription: string; }
const LVL_COLOR: Record<string, string> = { critical: "bg-red-500", high: "bg-orange-500", medium: "bg-yellow-500", low: "bg-green-500" };
export function ChangeRiskPanel({ score, level, tags, changeDescription }: ChangeRiskPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center ${LVL_COLOR[level] ?? "bg-gray-500"}`}>
        <div className="text-xl font-black">{score}/100 — {level.toUpperCase()}</div>
        <div className="text-xs opacity-80">{changeDescription}</div>
      </div>
      <div className="p-3 flex flex-wrap gap-1">
        {tags.map(t => <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800">{t}</span>)}
      </div>
    </div>
  );
}
