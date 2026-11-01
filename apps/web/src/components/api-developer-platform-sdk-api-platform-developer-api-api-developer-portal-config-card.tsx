"use client";

interface PortalInfo { portal_id: string; title: string; primary_color: string; sections: string[]; custom_domain: string; signup_enabled: boolean; }
interface Props { portals: PortalInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiDeveloperPortalConfigCard({ portals, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌐 Developer Portal</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {portals.length} portals</p>
      </div>
      {portals.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No portals configured</p>
      ) : (
        <div className="space-y-2">
          {portals.map((p) => (
            <div key={p.portal_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <span className="inline-block h-3 w-3 rounded-full" style={{ backgroundColor: p.primary_color }} />
                  <span className="font-medium text-gray-700 dark:text-gray-300">{p.title}</span>
                </div>
                {p.signup_enabled && <span className="text-[9px] text-green-600 dark:text-green-400">signups on</span>}
              </div>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {p.sections.map((s) => <span key={s} className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{s}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
