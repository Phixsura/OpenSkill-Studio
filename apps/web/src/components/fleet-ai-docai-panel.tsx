"use client";
export function FleetAiDocaiPanel({ services, active, pages, fields }: { services: number; active: number; pages: number; fields: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📄 AI Document</h3>
    <div className="text-sm">{active}/{services} active · {pages.toLocaleString()} pages · {fields.toLocaleString()} fields</div>
  </div>);
}
