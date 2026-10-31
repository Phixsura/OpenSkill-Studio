"use client";

interface InfoItem { label: string; value: string; icon: string; }
interface Link { label: string; url: string; icon: string; }
interface AppDetailSidebarProps { infoItems: InfoItem[]; links: Link[];
  permissions: string[]; tags: string[]; onTagClick?: (tag: string) => void; }

export function AppDetailSidebar({ infoItems, links, permissions, tags, onTagClick }: AppDetailSidebarProps) {
  return (
    <div className="space-y-5">
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-gray-400">Information</h3>
        {infoItems.map(item => (
          <div key={item.label} className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-1.5 text-gray-500">{item.icon} {item.label}</span>
            <span className="font-medium">{item.value}</span>
          </div>
        ))}
      </div>
      {links.length > 0 && (
        <div className="space-y-1.5">
          <h3 className="text-sm font-semibold text-gray-400">Links</h3>
          {links.map(link => (
            <a key={link.url} href={link.url.startsWith("http") || link.url.startsWith("mailto:") ? link.url : "#"} target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-sm text-blue-500 hover:underline">
              {link.icon} {link.label}
            </a>
          ))}
        </div>
      )}
      {permissions.length > 0 && (
        <div className="space-y-1.5">
          <h3 className="text-sm font-semibold text-gray-400">Permissions ({permissions.length})</h3>
          {permissions.map(p => (
            <div key={p} className="flex items-center gap-1.5 text-xs text-gray-500">
              <span className="text-green-500">✓</span> {p}
            </div>
          ))}
        </div>
      )}
      {tags.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-400">Tags</h3>
          <div className="mt-1.5 flex flex-wrap gap-1">
            {tags.map(t => (
              <button key={t} onClick={() => onTagClick?.(t)}
                className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs hover:bg-blue-50 dark:bg-gray-800">{t}</button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
