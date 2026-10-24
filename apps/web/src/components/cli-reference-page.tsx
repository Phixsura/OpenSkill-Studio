"use client";

interface Command { description: string; flags: string[]; }
interface CliReferencePageProps { groups: Record<string, Record<string, Command>>; }

export function CliReferencePage({ groups }: CliReferencePageProps) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">CLI Reference</h1>
      {Object.entries(groups).map(([group, commands]) => (
        <div key={group} className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
          <h2 className="text-lg font-semibold capitalize">{group}</h2>
          <div className="mt-3 space-y-2">
            {Object.entries(commands).map(([name, cmd]) => (
              <div key={name} className="rounded bg-gray-50 p-3 dark:bg-gray-800">
                <div className="flex items-baseline gap-2">
                  <code className="text-sm font-bold">openskill {group} {name}</code>
                  <span className="text-xs text-gray-400">{cmd.description}</span>
                </div>
                {cmd.flags.length > 0 && (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {cmd.flags.map(f => <code key={f} className="rounded bg-gray-200 px-1.5 py-0.5 text-xs dark:bg-gray-700">{f}</code>)}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
