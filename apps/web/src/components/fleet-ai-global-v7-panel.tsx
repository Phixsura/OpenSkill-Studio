"use client";
export function FleetAiGlobalV7Panel({ systems, active, regions, countries, languages }: { systems: number; active: number; regions: number; countries: number; languages: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 AI Global v7</h3>
    <div className="text-sm">{active}/{systems} active · {regions} regions · {countries} countries · {languages} languages</div>
  </div>);
}
