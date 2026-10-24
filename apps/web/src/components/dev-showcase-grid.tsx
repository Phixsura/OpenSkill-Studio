"use client";

interface ShowcaseDev { name: string; bio: string; appCount: number;
  installsDisplay: string; verified: boolean; spotlight: boolean; }
interface DevShowcaseGridProps { developers: ShowcaseDev[];
  onSelect: (name: string) => void; }

export function DevShowcaseGrid({ developers, onSelect }: DevShowcaseGridProps) {
  return (
    <div className="grid grid-cols-3 gap-4">
      {developers.map(d => (
        <button key={d.name} onClick={() => onSelect(d.name)}
          className={`rounded-xl border p-4 text-center hover:shadow-lg transition ${
            d.spotlight ? "border-yellow-300 dark:border-yellow-700 bg-yellow-50/30 dark:bg-yellow-900/10" : "dark:border-gray-700"
          }`}>
          <div className="w-12 h-12 rounded-full bg-blue-500 mx-auto mb-2 flex items-center justify-center text-white text-lg font-bold">
            {d.name[0]}
          </div>
          <div className="flex items-center justify-center gap-1 mb-1">
            <p className="text-sm font-bold">{d.name}</p>
            {d.verified && <span className="text-blue-500 text-xs">✓</span>}
            {d.spotlight && <span className="text-yellow-500 text-xs">⭐</span>}
          </div>
          <p className="text-xs text-gray-500 mb-2">{d.bio}</p>
          <div className="flex justify-center gap-3 text-xs text-gray-400">
            <span>📱 {d.appCount} apps</span>
            <span>📥 {d.installsDisplay}</span>
          </div>
        </button>
      ))}
    </div>
  );
}
