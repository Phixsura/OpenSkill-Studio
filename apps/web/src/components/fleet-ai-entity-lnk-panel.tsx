"use client";
export function FleetAiEntityLnkPanel({ linkers, active, entities, linked, accuracy }: { linkers: number; active: number; entities: number; linked: number; accuracy: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 AI Entity Linker</h3>
    <div className="text-sm">{active}/{linkers} active · {entities.toLocaleString()} entities · {linked.toLocaleString()} linked · {accuracy}% acc</div>
  </div>);
}
