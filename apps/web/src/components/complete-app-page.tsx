"use client";

interface Tab { id: string; label: string; icon: string; }
interface CompleteAppPageProps { heroName: string; heroIcon: string; heroTagline: string;
  heroDeveloper: string; tabs: Tab[]; activeTab: string; priceDisplay: string;
  onTabChange: (id: string) => void; onInstall: () => void; children: React.ReactNode; }

export function CompleteAppPage({ heroName, heroIcon, heroTagline, heroDeveloper,
  tabs, activeTab, priceDisplay, onTabChange, onInstall, children }: CompleteAppPageProps) {
  return (
    <div>
      <div className="flex items-start gap-4 mb-6">
        <span className="text-5xl">{heroIcon}</span>
        <div className="flex-1">
          <h1 className="text-2xl font-bold">{heroName}</h1>
          <p className="text-sm text-gray-500">{heroTagline}</p>
          <p className="text-xs text-gray-400">By {heroDeveloper}</p>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold mb-1">{priceDisplay}</p>
          <button onClick={onInstall}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">Install</button>
        </div>
      </div>
      <div className="flex border-b dark:border-gray-700 mb-6">
        {tabs.map(t => (
          <button key={t.id} onClick={() => onTabChange(t.id)}
            className={`px-4 py-2 text-sm border-b-2 ${
              t.id === activeTab ? "border-blue-500 text-blue-600 font-medium" : "border-transparent text-gray-500"
            }`}>{t.icon} {t.label}</button>
        ))}
      </div>
      <div>{children}</div>
    </div>
  );
}
