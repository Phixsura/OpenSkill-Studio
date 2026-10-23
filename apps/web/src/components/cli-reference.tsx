"use client";

interface CliCommand { command: string; description: string; usage: string; flagCount: number; }
interface CliReferenceProps { commands: CliCommand[]; }

export function CliReference({ commands }: CliReferenceProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">CLI Reference</h3>
      <div className="space-y-2">
        {commands.map(c => (
          <div key={c.command} className="rounded-lg border p-3 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <code className="text-sm font-mono font-bold text-blue-600">osk {c.command}</code>
              <span className="text-xs text-gray-400">{c.flagCount} flags</span>
            </div>
            <p className="mt-1 text-xs text-gray-500">{c.description}</p>
            <code className="mt-1 block text-xs text-gray-400 bg-gray-50 dark:bg-gray-800 px-2 py-1 rounded">{c.usage}</code>
          </div>
        ))}
      </div>
    </div>
  );
}
