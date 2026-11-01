"use client";
export function FleetAiModelAnnotPanel({ annotators, active, models, annotations, tags }: { annotators: number; active: number; models: number; annotations: number; tags: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏷️ AI Model Annotation</h3>
    <div className="text-sm">{active}/{annotators} active · {models} models · {annotations.toLocaleString()} annotations · {tags} tags</div>
  </div>);
}
