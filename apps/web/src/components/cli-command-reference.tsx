"use client";

interface Arg { name: string; type: string; required: boolean; description: string; }
interface Command { name: string; description: string; args: Arg[]; }
interface CliCommandReferenceProps { cliName: string; commands: Command[]; installCmd: string; }

export function CliCommandReference({ cliName, commands, installCmd }: CliCommandReferenceProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">CLI Reference</h2>
      <div className="rounded bg-gray-900 p-3 font-mono text-sm text-green-400">
        <p>$ {installCmd}</p>
        <p className="mt-1 text-gray-400">$ {cliName} --help</p>
      </div>
      <div className="space-y-3">
        {commands.map(cmd => (
          <div key={cmd.name} className="rounded-lg border p-3 dark:border-gray-700">
            <div className="flex items-baseline gap-2">
              <code className="font-mono font-bold text-blue-600">{cliName} {cmd.name}</code>
            </div>
            <p className="mt-0.5 text-sm text-gray-400">{cmd.description}</p>
            {cmd.args.length > 0 && (
              <div className="mt-2 space-y-1">
                {cmd.args.map(a => (
                  <div key={a.name} className="flex items-center gap-2 text-xs">
                    <code className="text-purple-500">{a.name}</code>
                    <span className="text-gray-400">({a.type})</span>
                    {a.required && <span className="text-red-400">required</span>}
                    {a.description && <span className="text-gray-300">— {a.description}</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
