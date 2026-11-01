"use client";
export function FleetAiOutParserPanel({ parsers, active, parsed, formats, success }: { parsers: number; active: number; parsed: number; formats: number; success: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Output Parser</h3>
    <div className="text-sm">{active}/{parsers} active · {parsed.toLocaleString()} parsed · {formats} formats · {success}% success</div>
  </div>);
}
