"use client";
import { useState } from "react";

interface CspDirective { name: string; sources: string[]; }
interface ViolationSummary { total: number; byDirective: Record<string, number>; topBlocked: Record<string, number>; }

export function CspPolicyEditor({ directives, violations, strict, onAddSource, onToggleStrict }: {
  directives: CspDirective[]; violations: ViolationSummary;
  strict: boolean; onAddSource?: (directive: string, source: string) => void;
  onToggleStrict?: (strict: boolean) => void;
}) {
  const [newDirective, setNewDirective] = useState("script-src");
  const [newSource, setNewSource] = useState("");

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-bold text-sm">Content Security Policy</h3>
        <label className="flex items-center gap-2 text-xs">
          <input type="checkbox" checked={strict} onChange={e => onToggleStrict?.(e.target.checked)} />
          <span className={strict ? "text-green-600 font-medium" : "text-yellow-600"}>
            {strict ? "🔒 Strict Mode" : "⚠️ Relaxed Mode"}
          </span>
        </label>
      </div>

      {/* Add source */}
      <div className="flex gap-2">
        <select value={newDirective} onChange={e => setNewDirective(e.target.value)}
          className="border dark:border-gray-700 rounded-lg px-2 py-1.5 text-xs bg-transparent font-mono">
          {["script-src", "style-src", "img-src", "connect-src", "font-src", "frame-src"].map(d =>
            <option key={d}>{d}</option>)}
        </select>
        <input value={newSource} onChange={e => setNewSource(e.target.value)} placeholder="https://cdn.example.com"
          className="flex-1 border dark:border-gray-700 rounded-lg px-2 py-1.5 text-xs bg-transparent font-mono" />
        <button onClick={() => { onAddSource?.(newDirective, newSource); setNewSource(""); }}
          className="text-xs bg-blue-500 text-white px-3 py-1.5 rounded-lg">Add</button>
      </div>

      {/* Directives */}
      <div className="space-y-1">
        {directives.map(d => (
          <div key={d.name} className="border dark:border-gray-700 rounded-lg p-2">
            <span className="text-xs font-mono font-bold text-blue-600">{d.name}</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {d.sources.map(s => (
                <span key={s} className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                  s.includes("unsafe") ? "bg-red-100 text-red-700" :
                  s.includes("nonce") ? "bg-purple-100 text-purple-700" :
                  "bg-gray-100 dark:bg-gray-800"
                }`}>{s}</span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Violations */}
      {violations.total > 0 && (
        <div className="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-xl p-3">
          <span className="text-xs font-bold text-red-600">🚨 {violations.total} CSP Violations</span>
          <div className="mt-1 space-y-0.5">
            {Object.entries(violations.topBlocked).map(([uri, count]) => (
              <div key={uri} className="text-[10px] font-mono text-red-500">
                {count}× blocked: {uri}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
