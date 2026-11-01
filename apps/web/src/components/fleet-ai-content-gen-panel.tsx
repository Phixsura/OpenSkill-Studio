"use client";
export function FleetAiContentGenPanel({ generators, active, content, words, quality }: { generators: number; active: number; content: number; words: number; quality: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✍️ AI Content Generator</h3>
    <div className="text-sm">{active}/{generators} active · {content.toLocaleString()} content · {words.toLocaleString()} words · {quality}% quality</div>
  </div>);
}
