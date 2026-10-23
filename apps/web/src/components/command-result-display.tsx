"use client";

interface CommandResultDisplayProps { command: string; exitCode: number; success: boolean;
  stdoutLines: string[]; stderrLines: string[]; durationFormatted: string; }

export function CommandResultDisplay({ command, exitCode, success, stdoutLines,
  stderrLines, durationFormatted }: CommandResultDisplayProps) {
  return (
    <div className="space-y-2 rounded-lg border dark:border-gray-700">
      <div className="flex items-center justify-between border-b px-4 py-2 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <span className={success ? "text-green-500" : "text-red-500"}>{success ? "✅" : "❌"}</span>
          <code className="text-sm font-bold">$ {command}</code>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span>exit {exitCode}</span>
          <span>{durationFormatted}</span>
        </div>
      </div>
      <div className="max-h-48 overflow-y-auto p-3 font-mono text-xs">
        {stdoutLines.map((line, i) => (
          <div key={`out-${i}`} className="text-gray-300">{line}</div>
        ))}
        {stderrLines.map((line, i) => (
          <div key={`err-${i}`} className="text-red-400">{line}</div>
        ))}
        {stdoutLines.length === 0 && stderrLines.length === 0 && (
          <span className="text-gray-500">No output</span>
        )}
      </div>
    </div>
  );
}
