"use client";

interface Country { code: string; name: string; }
interface GeoRestrictionMapProps { mode: string; countries: Country[];
  onToggleCountry: (code: string) => void; onChangeMode: (mode: string) => void; }

export function GeoRestrictionMap({ mode, countries, onToggleCountry, onChangeMode }: GeoRestrictionMapProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Geo Restrictions</h2>
        <div className="flex gap-1">
          {["allow", "block"].map(m => (
            <button key={m} onClick={() => onChangeMode(m)}
              className={`rounded px-3 py-1 text-xs capitalize ${mode === m ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
              {m}list
            </button>
          ))}
        </div>
      </div>
      <p className="text-sm text-gray-400">
        {mode === "allow" ? "Only available in" : "Blocked in"} {countries.length} countries
      </p>
      <div className="flex flex-wrap gap-2">
        {countries.map(c => (
          <button key={c.code} onClick={() => onToggleCountry(c.code)}
            className={`rounded-full border px-3 py-1 text-sm ${mode === "allow" ? "border-green-300 bg-green-50 dark:border-green-700 dark:bg-green-900/10" : "border-red-300 bg-red-50 dark:border-red-700 dark:bg-red-900/10"}`}>
            {c.code} — {c.name} ×
          </button>
        ))}
      </div>
      {countries.length === 0 && (
        <p className="text-sm text-gray-400">{mode === "allow" ? "Available everywhere (no restrictions)" : "No countries blocked"}</p>
      )}
    </div>
  );
}
