"use client";

interface SlashCommand { command: string; description: string; usage: string; }
interface SlashCommandHelpProps { commands: SlashCommand[]; }

export function SlashCommandHelp({ commands }: SlashCommandHelpProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Slash Commands</h3>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {commands.map(c => (
          <div key={c.command} className="px-4 py-2.5">
            <div className="flex items-center gap-2">
              <code className="text-sm font-mono font-bold text-blue-600">{c.command}</code>
              <span className="text-xs text-gray-500">{c.description}</span>
            </div>
            <code className="mt-1 block text-xs text-gray-400 font-mono">{c.usage}</code>
          </div>
        ))}
      </div>
    </div>
  );
}
