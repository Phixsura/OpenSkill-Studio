"use client";

import { useState } from "react";

interface ModuleImport {
  moduleName: string;
  allowed: boolean;
  reason: string;
}

interface AllowlistInfo {
  builtin: string[];
  custom: string[];
  blocked: string[];
}

export function ModuleLoaderPanel({
  importLog,
  allowlist,
  blockedCount,
  onAddModule,
  onTestImport,
}: {
  importLog: ModuleImport[];
  allowlist: AllowlistInfo;
  blockedCount: number;
  onAddModule?: (module: string) => void;
  onTestImport?: (module: string) => void;
}) {
  const [tab, setTab] = useState<"log" | "allowlist" | "blocked">("log");
  const [testModule, setTestModule] = useState("");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📦 Module Loader</h2>
        {blockedCount > 0 && (
          <span className="text-xs bg-red-600 text-white px-2 py-0.5 rounded-full">{blockedCount} blocked</span>
        )}
      </div>

      <div className="flex gap-2">
        <input type="text" value={testModule} onChange={(e) => setTestModule(e.target.value)}
          placeholder="Test module import..."
          className="flex-1 rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm font-mono" />
        <button onClick={() => { onTestImport?.(testModule); setTestModule(""); }}
          className="text-xs bg-blue-600 text-white px-3 py-1.5 rounded-lg">Test</button>
        <button onClick={() => { onAddModule?.(testModule); setTestModule(""); }}
          className="text-xs bg-green-600 text-white px-3 py-1.5 rounded-lg">Allow</button>
      </div>

      <div className="flex gap-1">
        {(["log", "allowlist", "blocked"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-xs px-3 py-1 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t === "log" ? `Import Log (${importLog.length})` : t === "allowlist" ? "Allowed" : `Blocked (${allowlist.blocked.length})`}
          </button>
        ))}
      </div>

      {tab === "log" && (
        <div className="space-y-0.5">
          {importLog.map((entry, i) => (
            <div key={i} className="flex items-center gap-2 text-xs rounded-lg border dark:border-gray-700 p-2">
              <span className={entry.allowed ? "text-green-600" : "text-red-500"}>{entry.allowed ? "✅" : "🚫"}</span>
              <code className="font-semibold">{entry.moduleName}</code>
              <span className="text-gray-400">{entry.reason}</span>
            </div>
          ))}
        </div>
      )}

      {tab === "allowlist" && (
        <div className="space-y-2">
          <div>
            <span className="text-xs font-semibold text-gray-500">Built-in ({allowlist.builtin.length})</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {allowlist.builtin.slice(0, 20).map((m) => (
                <span key={m} className="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 px-1.5 py-0.5 rounded">{m}</span>
              ))}
              {allowlist.builtin.length > 20 && <span className="text-xs text-gray-400">+{allowlist.builtin.length - 20} more</span>}
            </div>
          </div>
          {allowlist.custom.length > 0 && (
            <div>
              <span className="text-xs font-semibold text-gray-500">Custom ({allowlist.custom.length})</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {allowlist.custom.map((m) => (
                  <span key={m} className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 px-1.5 py-0.5 rounded">{m}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {tab === "blocked" && (
        <div className="flex flex-wrap gap-1">
          {allowlist.blocked.map((m) => (
            <span key={m} className="text-xs bg-red-100 dark:bg-red-900/30 text-red-600 px-1.5 py-0.5 rounded">{m}</span>
          ))}
        </div>
      )}
    </div>
  );
}
