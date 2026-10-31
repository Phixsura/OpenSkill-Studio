"use client";

interface CliCommand { command: string; copyable: string; }
interface CliReferenceCardProps { title: string; commands: CliCommand[];
  onCopy: (cmd: string) => void; }

export function CliReferenceCard({ title, commands, onCopy }: CliReferenceCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">💻 {title}</h3>
      <div className="space-y-2">
        {commands.map((c, i) => (
          <div key={i} className="flex items-center justify-between bg-gray-900 rounded-lg px-4 py-2.5">
            <code className="text-sm text-green-400 font-mono truncate">{c.command}</code>
            <button onClick={() => onCopy(c.copyable)}
              className="text-xs text-gray-400 hover:text-white ml-2 shrink-0">📋</button>
          </div>
        ))}
      </div>
    </div>
  );
}
