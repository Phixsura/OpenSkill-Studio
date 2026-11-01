"use client";

interface Guide { id: string; title: string; icon: string; stepCount: number; steps?: string[]; }
interface GettingStartedGuideProps { guides: Guide[]; recommended: string;
  onSelect: (id: string) => void; }

export function GettingStartedGuide({ guides, recommended, onSelect }: GettingStartedGuideProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🎓 Getting Started</h3>
      <div className="space-y-2">
        {guides.map(g => (
          <button key={g.id} onClick={() => onSelect(g.id)}
            className={`w-full text-left flex items-center gap-3 rounded-lg px-4 py-3 transition ${
              g.id === recommended ? "bg-blue-50 dark:bg-blue-900/20 ring-1 ring-blue-200" :
              "bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700"
            }`}>
            <span className="text-2xl">{g.icon}</span>
            <div>
              <p className="text-sm font-medium">{g.title}</p>
              <p className="text-xs text-gray-400">{g.stepCount} steps</p>
            </div>
            {g.id === recommended && <span className="ml-auto text-xs text-blue-600 font-medium">Recommended</span>}
          </button>
        ))}
      </div>
    </div>
  );
}
