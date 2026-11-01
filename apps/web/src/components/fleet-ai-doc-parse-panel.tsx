"use client";
export function FleetAiDocParsePanel({ parsers, active, docs, fields, accuracy }: { parsers: number; active: number; docs: number; fields: number; accuracy: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📑 AI Document Parsing</h3>
    <div className="text-sm">{active}/{parsers} active · {docs.toLocaleString()} docs · {fields.toLocaleString()} fields · {accuracy}% acc</div>
  </div>);
}
