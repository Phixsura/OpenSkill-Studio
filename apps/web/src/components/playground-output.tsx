"use client";

interface PlaygroundOutputProps { stdout: string; stderr: string; exitCode: number;
  success: boolean; executionMs: number; }

export function PlaygroundOutput({ stdout, stderr, exitCode, success, executionMs }: PlaygroundOutputProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Output</h3>
        <div className="flex items-center gap-2 text-xs">
          <span className={success ? "text-green-600" : "text-red-600"}>
            {success ? "✓" : "✗"} exit {exitCode}
          </span>
          <span className="text-gray-400">{executionMs}ms</span>
        </div>
      </div>
      {stdout && (
        <pre className="rounded-lg bg-gray-950 p-3 text-xs font-mono text-green-400 overflow-x-auto max-h-48">{stdout}</pre>
      )}
      {stderr && (
        <pre className="rounded-lg bg-red-950 p-3 text-xs font-mono text-red-400 overflow-x-auto max-h-32">{stderr}</pre>
      )}
      {!stdout && !stderr && (
        <p className="py-4 text-center text-sm text-gray-400">No output</p>
      )}
    </div>
  );
}
