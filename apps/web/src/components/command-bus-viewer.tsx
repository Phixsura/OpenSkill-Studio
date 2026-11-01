"use client";

interface CommandEntry { command: string; handler: string; status: string; }
interface CommandBusViewerProps { history: CommandEntry[]; totalDispatched: number;
  registeredCommands: number; byCommand: Record<string, number>; }

export function CommandBusViewer({ history, totalDispatched, registeredCommands, byCommand }: CommandBusViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📮 Command Bus</h3>
        <span className="text-xs text-gray-400">{registeredCommands} commands · {totalDispatched} dispatched</span>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-40 overflow-y-auto">
        {history.map((h, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-mono text-blue-500">{h.command}</span>
              <span className="text-gray-400">→ {h.handler}</span>
            </div>
            <span className="text-green-600">{h.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
