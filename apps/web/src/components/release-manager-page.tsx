"use client";

interface ReleaseManagerPageProps { appName: string; version: string; stage: string;
  stages: string[]; changelog: string; breaking: boolean;
  onAdvance: () => void; onEdit: () => void; }

const stageColors: Record<string, string> = {
  draft: "bg-gray-200", testing: "bg-blue-200", review: "bg-yellow-200",
  approved: "bg-green-200", published: "bg-green-500 text-white",
};

export function ReleaseManagerPage({ appName, version, stage, stages, changelog,
  breaking, onAdvance, onEdit }: ReleaseManagerPageProps) {
  const stageIdx = stages.indexOf(stage);
  const isFinal = stage === "published";
  return (
    <div className="mx-auto max-w-lg space-y-5">
      <h2 className="text-lg font-bold">📦 Release {appName} v{version}</h2>
      {breaking && <span className="rounded bg-red-100 px-2 py-0.5 text-xs text-red-700 dark:bg-red-900/30">💥 Breaking Change</span>}
      <div className="flex justify-between">
        {stages.map((s, i) => (
          <div key={s} className="flex flex-col items-center gap-1">
            <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-medium ${i <= stageIdx ? stageColors[s] ?? "bg-gray-200" : "bg-gray-100 dark:bg-gray-800"}`}>
              {i < stageIdx ? "✓" : i + 1}
            </div>
            <span className={`text-xs capitalize ${i === stageIdx ? "font-bold" : "text-gray-400"}`}>{s}</span>
          </div>
        ))}
      </div>
      <div className="rounded-lg bg-gray-50 p-3 dark:bg-gray-800">
        <p className="text-xs font-semibold text-gray-400 mb-1">Changelog</p>
        <p className="text-sm">{changelog}</p>
      </div>
      <div className="flex gap-2">
        <button onClick={onEdit} className="flex-1 rounded border py-2 text-sm dark:border-gray-700">Edit</button>
        {!isFinal && <button onClick={onAdvance} className="flex-1 rounded bg-blue-600 py-2 text-sm text-white">
          Advance to {stages[stageIdx + 1]}
        </button>}
        {isFinal && <span className="flex-1 text-center py-2 text-sm text-green-600 font-medium">✅ Published!</span>}
      </div>
    </div>
  );
}
