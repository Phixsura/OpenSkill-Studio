"use client";

interface NavItem {
  label: string;
  href: string;
}

interface NavSectionInfo {
  section_id: string;
  title: string;
  items: NavItem[];
}

interface DeveloperPortalCardProps {
  portalName: string;
  themeColor: string;
  welcomeMessage: string;
  sections: NavSectionInfo[];
  appName: string;
}

export default function DeveloperPortalCard({
  portalName,
  themeColor,
  welcomeMessage,
  sections,
  appName,
}: DeveloperPortalCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🏠 Developer Portal
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full" style={{ backgroundColor: themeColor }} />
          <span className="text-xs text-gray-400">{sections.length} sections</span>
        </div>
      </div>

      <div className="mb-3 rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
        <p className="text-xs font-medium text-gray-800 dark:text-gray-200">{portalName}</p>
        {welcomeMessage && <p className="mt-0.5 text-[10px] text-gray-400">{welcomeMessage}</p>}
      </div>

      {sections.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No navigation sections</p>
      ) : (
        <div className="space-y-2">
          {sections.map((s) => (
            <div key={s.section_id}>
              <p className="text-[10px] font-medium text-gray-500">{s.title}</p>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {s.items.map((item) => (
                  <span
                    key={item.href}
                    className="rounded bg-gray-100 px-1.5 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800"
                  >
                    {item.label}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
