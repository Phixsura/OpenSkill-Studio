"use client";

interface ItemInfo { item_id: string; title: string; completed: boolean; required: boolean; }
interface Props { items: ItemInfo[]; completionPct: number; allRequiredDone: boolean; developerName: string; appName: string; }

export default function APIDeveloperAPIApiOnboardingChecklistCard({ items, completionPct, allRequiredDone, developerName, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚀 Onboarding Checklist</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {developerName}</p>
        </div>
        <div className="text-right">
          <span className={`text-sm font-bold ${completionPct === 100 ? "text-green-600" : "text-blue-600"}`}>{completionPct}%</span>
          {allRequiredDone && <p className="text-[9px] text-green-500">✓ Ready</p>}
        </div>
      </div>
      <div className="mb-2 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
        <div className="h-1.5 rounded-full bg-blue-500" style={{ width: `${completionPct}%` }} />
      </div>
      <div className="space-y-1">
        {items.map((i) => (
          <div key={i.item_id} className="flex items-center gap-2 text-[11px]">
            <span className={i.completed ? "text-green-500" : "text-gray-300"}>{i.completed ? "✓" : "○"}</span>
            <span className={`${i.completed ? "text-gray-400 line-through" : "text-gray-700 dark:text-gray-300"}`}>{i.title}</span>
            {!i.required && <span className="text-[9px] text-gray-400">(optional)</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
