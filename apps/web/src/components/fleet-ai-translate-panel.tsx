"use client";
export function FleetAiTranslatePanel({ translators, active, translations, langPairs, bleu }: { translators: number; active: number; translations: number; langPairs: number; bleu: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 AI Translation</h3>
    <div className="text-sm">{active}/{translators} active · {translations.toLocaleString()} translations · {langPairs} pairs · BLEU {bleu}</div>
  </div>);
}
