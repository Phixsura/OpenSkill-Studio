"use client";
export function FleetAiOcrPanel({ services, active, pages, accuracy }: { services: number; active: number; pages: number; accuracy: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📄 AI OCR</h3>
    <div className="text-sm">{active}/{services} active · {pages.toLocaleString()} pages · {accuracy}% accuracy</div>
  </div>);
}
