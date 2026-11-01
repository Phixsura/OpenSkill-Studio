"use client";
export function FleetAiModelAdaptPanel({ adapters, active, providers, translations }: { adapters: number; active: number; providers: number; translations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 AI Model Adapter</h3>
    <div className="text-sm">{active}/{adapters} active · {providers} providers · {translations.toLocaleString()} translations</div>
  </div>);
}
