"use client";

import { useState } from "react";

interface ApiContract {
  id: string;
  provider: string;
  consumer: string;
  endpoint: string;
  method: string;
  fieldCount: number;
}

interface ContractTestResult {
  contractId: string;
  result: "pass" | "fail" | "warn";
  violations: string[];
  warnings: string[];
}

interface Compatibility {
  provider: string;
  consumer: string;
  contracts: number;
  passed: number;
  failed: number;
  compatible: boolean;
}

const resultConfig: Record<string, { color: string; icon: string }> = {
  pass: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "✅" },
  fail: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "❌" },
  warn: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "⚠️" },
};

const methodColors: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600",
  DELETE: "text-red-600", PATCH: "text-purple-600",
};

export function ContractTestPanel({
  contracts,
  results,
  compatibility,
  onRunTest,
}: {
  contracts: ApiContract[];
  results: ContractTestResult[];
  compatibility: Compatibility | null;
  onRunTest?: (contractId: string) => void;
}) {
  const [tab, setTab] = useState<"contracts" | "results">("contracts");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📋 Contract Tests</h2>
        {compatibility && (
          <span className={`text-sm font-bold ${compatibility.compatible ? "text-green-600" : "text-red-600"}`}>
            {compatibility.compatible ? "✅ Compatible" : "❌ Incompatible"}
          </span>
        )}
      </div>

      <div className="flex gap-1">
        <button onClick={() => setTab("contracts")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "contracts" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Contracts ({contracts.length})
        </button>
        <button onClick={() => setTab("results")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "results" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Results ({results.length})
        </button>
      </div>

      {tab === "contracts" && (
        <div className="space-y-1">
          {contracts.map((ct) => (
            <div key={ct.id} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm">
                <span className={`font-bold ${methodColors[ct.method] || ""}`}>{ct.method}</span>
                <code>{ct.endpoint}</code>
                <span className="text-xs text-gray-400">{ct.provider} → {ct.consumer}</span>
                <span className="text-xs text-gray-400">{ct.fieldCount} fields</span>
              </div>
              <button onClick={() => onRunTest?.(ct.id)}
                className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Test</button>
            </div>
          ))}
        </div>
      )}

      {tab === "results" && (
        <div className="space-y-1">
          {results.map((r, i) => {
            const cfg = resultConfig[r.result];
            return (
              <div key={i} className="rounded-lg border dark:border-gray-700 p-3">
                <div className="flex items-center gap-2 mb-1">
                  <span>{cfg.icon}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{r.result}</span>
                  <code className="text-xs text-gray-500">{r.contractId}</code>
                </div>
                {r.violations.map((v, j) => <div key={j} className="text-xs text-red-500">• {v}</div>)}
                {r.warnings.map((w, j) => <div key={j} className="text-xs text-yellow-600">• {w}</div>)}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
