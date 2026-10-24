"use client";
export function FleetAiParaphrasePanel({ engines, active, paraphrased, quality, diversity }: { engines: number; active: number; paraphrased: number; quality: number; diversity: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI Paraphraser</h3>
    <div className="text-sm">{active}/{engines} active · {paraphrased.toLocaleString()} paraphrased · {quality}% quality · {diversity} diversity</div>
  </div>);
}
