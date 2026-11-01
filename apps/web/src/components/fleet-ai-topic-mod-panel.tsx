"use client";
export function FleetAiTopicModPanel({ modelers, active, docs, topics, coherence }: { modelers: number; active: number; docs: number; topics: number; coherence: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Topic Modeler</h3>
    <div className="text-sm">{active}/{modelers} active · {docs.toLocaleString()} docs · {topics} topics · coherence {coherence}</div>
  </div>);
}
