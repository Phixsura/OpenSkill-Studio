"use client";

interface Tier { id: string; label: string; icon: string; feeDisplay: string;
  benefits: string[]; recommended: boolean; }
interface DevProgramTiersProps { tiers: Tier[]; currentTier: string;
  onSelect: (id: string) => void; }

export function DevProgramTiers({ tiers, currentTier, onSelect }: DevProgramTiersProps) {
  return (
    <div className="grid grid-cols-4 gap-4">
      {tiers.map(t => (
        <div key={t.id} className={`rounded-xl border p-5 ${
          t.id === currentTier ? "border-blue-500 ring-2 ring-blue-200" :
          t.recommended ? "border-green-300" : "dark:border-gray-700"
        }`}>
          <div className="text-center mb-3">
            <span className="text-3xl">{t.icon}</span>
            <h4 className="font-bold mt-1">{t.label}</h4>
            <p className="text-lg font-bold">{t.feeDisplay}</p>
            {t.recommended && <span className="text-xs text-green-600">Recommended</span>}
          </div>
          <ul className="text-xs text-gray-500 space-y-1 mb-4">
            {t.benefits.map(b => <li key={b}>✓ {b}</li>)}
          </ul>
          <button onClick={() => onSelect(t.id)}
            className={`w-full py-2 text-sm rounded-lg ${
              t.id === currentTier ? "bg-gray-200 text-gray-500" : "bg-blue-600 text-white hover:bg-blue-700"
            }`}>{t.id === currentTier ? "Current" : "Select"}</button>
        </div>
      ))}
    </div>
  );
}
