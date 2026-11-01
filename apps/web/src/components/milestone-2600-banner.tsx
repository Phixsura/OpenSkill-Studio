"use client";

export function Milestone2600Banner() {
  return (
    <div className="rounded-xl border-2 border-yellow-500 bg-gradient-to-r from-yellow-50 to-amber-50 dark:from-yellow-900/10 dark:to-amber-900/10 p-6 text-center">
      <div className="text-4xl mb-2">🏆🎊🏆</div>
      <h2 className="text-2xl font-bold text-yellow-700 dark:text-yellow-400">2,600 Commits · 224K Lines!</h2>
      <p className="text-sm text-gray-500 mt-1">OpenSkill Developer Platform — Fully Operational</p>
      <div className="flex justify-center gap-6 mt-4 text-sm">
        <div><span className="text-xl font-bold text-yellow-700">7,550+</span><div className="text-[10px] text-gray-400">Files</div></div>
        <div><span className="text-xl font-bold text-yellow-700">1,300+</span><div className="text-[10px] text-gray-400">Services</div></div>
        <div><span className="text-xl font-bold text-yellow-700">10</span><div className="text-[10px] text-gray-400">Modules</div></div>
      </div>
    </div>
  );
}
