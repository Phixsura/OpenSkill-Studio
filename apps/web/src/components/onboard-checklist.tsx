"use client";

interface CheckItem { id: string; title: string; category: string;
  required: boolean; completed: boolean; }
interface OnboardChecklistProps { items: CheckItem[]; progressPct: number;
  readyToContribute: boolean; onComplete: (id: string) => void; }

export function OnboardChecklist({ items, progressPct, readyToContribute, onComplete }: OnboardChecklistProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Onboarding</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{progressPct}%</span>
          <span className={readyToContribute ? "text-green-600" : "text-yellow-600"}>
            {readyToContribute ? "✅ Ready" : "⏳ In Progress"}
          </span>
        </div>
      </div>
      <div className="p-3 border-b dark:border-gray-700">
        <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
          <div className={`h-full rounded-full ${progressPct === 100 ? "bg-green-500" : "bg-blue-500"}`}
            style={{ width: `${progressPct}%` }} />
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {items.map(i => (
          <div key={i.id} className={`flex items-center justify-between px-4 py-2 ${i.completed ? "opacity-60" : ""}`}>
            <div className="flex items-center gap-2">
              <button onClick={() => !i.completed && onComplete(i.id)}
                className={`w-5 h-5 rounded border flex items-center justify-center text-[10px] ${i.completed ? "bg-green-500 border-green-500 text-white" : "border-gray-300"}`}>
                {i.completed ? "✓" : ""}
              </button>
              <span className="text-sm">{i.title}</span>
              {i.required && <span className="text-[10px] text-red-400">required</span>}
            </div>
            <span className="text-[10px] text-gray-400">{i.category}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
