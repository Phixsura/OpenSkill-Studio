"use client";
export function FleetMemoryProfilerV9Panel({ apps, leaks }: { apps: number; leaks: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧠 Memory Profiler v9</h3>
    <div className="text-sm">{apps} apps · {leaks} leaks</div>
  </div>);
}
