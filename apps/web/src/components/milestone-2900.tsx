"use client";

export function Milestone2900() {
  return (
    <div className="rounded-xl border-2 border-yellow-500 bg-gradient-to-br from-yellow-50 to-amber-50 dark:from-yellow-950 dark:to-amber-950 overflow-hidden">
      <div className="p-6 text-center">
        <div className="text-4xl mb-2">🏆</div>
        <h2 className="text-xl font-bold mb-1">2,900 Commits!</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">249K Lines · 8,620+ Files</p>
        <div className="mt-4 grid grid-cols-3 gap-3 text-xs">
          <div className="bg-white/50 dark:bg-black/20 rounded-lg p-2">
            <div className="font-bold text-lg text-yellow-600">1,470+</div>
            <div className="text-gray-500">Services</div>
          </div>
          <div className="bg-white/50 dark:bg-black/20 rounded-lg p-2">
            <div className="font-bold text-lg text-yellow-600">1,470+</div>
            <div className="text-gray-500">Components</div>
          </div>
          <div className="bg-white/50 dark:bg-black/20 rounded-lg p-2">
            <div className="font-bold text-lg text-yellow-600">2,950+</div>
            <div className="text-gray-500">Tests</div>
          </div>
        </div>
        <div className="mt-3 text-xs text-amber-700 dark:text-amber-400 font-bold">
          🎯 Next: 250,000 LINES — QUARTER MILLION!
        </div>
      </div>
    </div>
  );
}
