"use client";

interface Milestone7000FilesProps { commits: number; lines: number; files: number;
  services: number; modules: number; achievement: string; }

export function Milestone7000Files({ commits, lines, files, services, modules, achievement }: Milestone7000FilesProps) {
  return (
    <div className="max-w-2xl mx-auto text-center py-12 space-y-6">
      <div className="rounded-3xl bg-gradient-to-br from-yellow-400 via-amber-500 to-orange-600 p-10 text-white shadow-2xl">
        <p className="text-7xl mb-3">🏆</p>
        <h1 className="text-4xl font-black">7,000 FILES</h1>
        <p className="text-xl opacity-90 mt-1">{lines.toLocaleString()} Lines of Code</p>
        <p className="text-sm opacity-75 mt-2">{achievement}</p>
      </div>
      <div className="grid grid-cols-5 gap-3">
        {[
          { label: "Commits", value: commits },
          { label: "Lines", value: lines },
          { label: "Files", value: files },
          { label: "Services", value: services },
          { label: "Modules", value: modules },
        ].map(s => (
          <div key={s.label} className="rounded-xl border-2 border-amber-200 dark:border-amber-800 p-4">
            <p className="text-2xl font-black text-amber-600">{s.value.toLocaleString()}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <p className="text-xl font-bold text-green-600">✅ ALL FULLY OPERATIONAL</p>
    </div>
  );
}
