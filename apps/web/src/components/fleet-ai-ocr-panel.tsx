"use client";
export function FleetAiOcrPanel({ engines, active, pages, accuracy, languages }: { engines: number; active: number; pages: number; accuracy: number; languages: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📷 AI OCR</h3>
    <div className="text-sm">{active}/{engines} active · {pages.toLocaleString()} pages · {accuracy}% acc · {languages} langs</div>
  </div>);
}
