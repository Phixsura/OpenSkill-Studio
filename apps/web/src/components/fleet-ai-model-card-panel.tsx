"use client";
export function FleetAiModelCardPanel({ cards, active, models, completeness, sections }: { cards: number; active: number; models: number; completeness: number; sections: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Model Card</h3>
    <div className="text-sm">{active}/{cards} active · {models} models · {completeness}% complete · {sections} sections</div>
  </div>);
}
