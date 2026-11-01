"use client";
export function FleetAiModelMergePanel({ mergers, active, merges, methods, improvement }: { mergers: number; active: number; merges: number; methods: string[]; improvement: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 AI Model Merging</h3>
    <div className="text-sm">{active}/{mergers} active · {merges} merges · {methods.join(", ")} · +{improvement}%</div>
  </div>);
}
