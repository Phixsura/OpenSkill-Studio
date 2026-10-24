"use client";

interface GuideSection { id: string; title: string; icon: string; estimatedMin: number;
  completed: boolean; topicCount: number; topics: string[]; }
interface DeveloperGuideNavProps { sections: GuideSection[]; progressPct: number;
  totalReadingMin: number; onSelect: (id: string) => void; }

export function DeveloperGuideNav({ sections, progressPct, totalReadingMin, onSelect }: DeveloperGuideNavProps) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-bold">📚 Developer Guide</h2>
        <div className="mt-2 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className="h-full rounded-full bg-green-500 transition-all" style={{ width: `${progressPct}%` }} />
        </div>
        <p className="mt-1 text-xs text-gray-400">{progressPct}% complete · ~{totalReadingMin} min reading</p>
      </div>
      <div className="space-y-1">
        {sections.map(s => (
          <button key={s.id} onClick={() => onSelect(s.id)}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left ${s.completed ? "opacity-60" : "hover:bg-gray-50 dark:hover:bg-gray-800"}`}>
            <span className={`flex h-7 w-7 items-center justify-center rounded-full text-sm ${s.completed ? "bg-green-500 text-white" : "bg-gray-200 dark:bg-gray-700"}`}>
              {s.completed ? "✓" : s.icon}
            </span>
            <div className="flex-1">
              <p className={`text-sm font-medium ${s.completed ? "line-through text-gray-400" : ""}`}>{s.title}</p>
              <p className="text-xs text-gray-400">{s.topicCount} topics{s.estimatedMin > 0 ? ` · ~${s.estimatedMin} min` : ""}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
