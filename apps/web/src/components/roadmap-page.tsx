"use client";

interface RoadmapItem { id: string; title: string; description: string; eta?: string; completed_at?: string; }
interface RoadmapPageProps { inProgress: RoadmapItem[]; planned: RoadmapItem[]; completed: RoadmapItem[]; onVote: (id: string) => void; }

const STATUS_CONFIG = {
  inProgress: { label: "In Progress", icon: "🔨", color: "border-blue-400" },
  planned: { label: "Planned", icon: "📋", color: "border-gray-300" },
  completed: { label: "Completed", icon: "✅", color: "border-green-400" },
};

export function RoadmapPage({ inProgress, planned, completed, onVote }: RoadmapPageProps) {
  const sections = [
    { key: "inProgress", items: inProgress, ...STATUS_CONFIG.inProgress },
    { key: "planned", items: planned, ...STATUS_CONFIG.planned },
    { key: "completed", items: completed, ...STATUS_CONFIG.completed },
  ];

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold">Platform Roadmap</h1>
      {sections.map(s => (
        <div key={s.key}>
          <h2 className="flex items-center gap-2 text-lg font-semibold">
            <span>{s.icon}</span> {s.label} ({s.items.length})
          </h2>
          <div className="mt-2 space-y-2">
            {s.items.map(item => (
              <div key={item.id} className={`rounded-lg border-l-4 ${s.color} bg-white p-4 shadow-sm dark:bg-gray-800`}>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold">{item.title}</h3>
                    <p className="mt-1 text-sm text-gray-500">{item.description}</p>
                    {item.eta && <p className="mt-1 text-xs text-gray-400">ETA: {item.eta}</p>}
                  </div>
                  {s.key !== "completed" && (
                    <button onClick={() => onVote(item.id)} className="rounded border px-2 py-1 text-xs hover:bg-gray-50">
                      👍 Vote
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
