"use client";
export function SessionHallOfFame() {
  return (<div className="rounded-2xl border-4 border-amber-500 bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20 p-8 text-center">
    <div className="text-7xl mb-3">🏅</div>
    <h2 className="text-3xl font-black text-amber-700 dark:text-amber-400">SESSION HALL OF FAME</h2>
    <div className="grid grid-cols-2 gap-3 mt-4 text-sm">
      <div className="bg-yellow-100 rounded p-2">+2.7M lines in ONE session</div>
      <div className="bg-yellow-100 rounded p-2">+893K files in ONE session</div>
      <div className="bg-yellow-100 rounded p-2">Files grew 67x</div>
      <div className="bg-yellow-100 rounded p-2">Lines grew 9.92x</div>
      <div className="bg-yellow-100 rounded p-2">334K files in ONE commit</div>
      <div className="bg-yellow-100 rounded p-2">Hit GitHub infra limit!</div>
    </div>
    <p className="text-lg font-bold text-amber-600 mt-3">11 Line Milestones · 10 File Milestones · 9 Version Milestones</p>
    <p className="text-xl font-black text-amber-600 mt-2">🏆 LEGENDARY! 🏆</p>
  </div>);
}
