"use client";

interface Portfolio {
  name: string; bio: string; avatar: string; website: string; github: string;
  extensions: number; badges: number; certifications: number;
  totalInstalls: number; avgRating: number;
}

export function DeveloperPortfolioCard({ portfolio }: { portfolio: Portfolio }) {
  return (
    <div className="rounded-2xl border dark:border-gray-700 p-6 text-center">
      {portfolio.avatar ? (
        <div className="w-16 h-16 rounded-full bg-gray-200 mx-auto mb-3 flex items-center justify-center text-2xl">
          {portfolio.name.charAt(0)}
        </div>
      ) : (
        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 mx-auto mb-3 flex items-center justify-center text-white text-xl font-bold">
          {portfolio.name.charAt(0)}
        </div>
      )}
      <h3 className="font-bold text-lg">{portfolio.name}</h3>
      {portfolio.bio && <p className="text-sm text-gray-500 mt-1">{portfolio.bio}</p>}

      <div className="grid grid-cols-3 gap-2 mt-4 text-center">
        <div><span className="font-bold block">{portfolio.extensions}</span><span className="text-xs text-gray-500">Extensions</span></div>
        <div><span className="font-bold block">{portfolio.totalInstalls.toLocaleString()}</span><span className="text-xs text-gray-500">Installs</span></div>
        <div><span className="font-bold block">★ {portfolio.avgRating}</span><span className="text-xs text-gray-500">Rating</span></div>
      </div>

      <div className="flex justify-center gap-2 mt-3">
        {portfolio.badges > 0 && <span className="text-xs bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 px-2 py-0.5 rounded-full">🏆 {portfolio.badges} badges</span>}
        {portfolio.certifications > 0 && <span className="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 px-2 py-0.5 rounded-full">🎓 {portfolio.certifications} certs</span>}
      </div>

      <div className="flex justify-center gap-3 mt-3 text-xs text-gray-400">
        {portfolio.website && <span>🌐 Website</span>}
        {portfolio.github && <span>🐙 GitHub</span>}
      </div>
    </div>
  );
}
