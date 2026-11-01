"use client";

import { useState } from "react";

interface PlaygroundSessionProps { sessionId: string; language: string;
  onRun: (code: string) => { output: string; executionMs: number; memoryMb: number }; }

export function PlaygroundSession({ sessionId, language, onRun }: PlaygroundSessionProps) {
  const [code, setCode] = useState("");
  const [result, setResult] = useState<{ output: string; executionMs: number; memoryMb: number } | null>(null);

  const run = () => { if (code.trim()) setResult(onRun(code)); };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Playground</h3>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span className="rounded bg-blue-100 px-1.5 py-0.5 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">{language}</span>
          <code>{sessionId.slice(0, 12)}...</code>
        </div>
      </div>
      <textarea value={code} onChange={e => setCode(e.target.value)} rows={6}
        placeholder={`Write ${language} code here...`}
        className="w-full rounded-lg border bg-gray-950 p-3 text-sm font-mono text-green-400 dark:border-gray-700" />
      <button onClick={run} className="rounded bg-green-600 px-4 py-2 text-sm text-white font-medium">▶ Run</button>
      {result && (
        <div className="rounded-lg bg-gray-100 p-3 dark:bg-gray-800">
          <pre className="text-sm font-mono">{result.output}</pre>
          <div className="mt-2 flex gap-3 text-xs text-gray-400">
            <span>{result.executionMs}ms</span>
            <span>{result.memoryMb}MB</span>
          </div>
        </div>
      )}
    </div>
  );
}
