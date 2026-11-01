"use client";

interface OrgItem { id: string; name: string; role: string; plan: string; active: boolean; }
interface OrgSwitcherProps { orgs: OrgItem[]; currentName: string;
  onSwitch: (orgId: string) => void; onCreate: () => void; canCreate: boolean; }

export function OrgSwitcher({ orgs, currentName, onSwitch, onCreate, canCreate }: OrgSwitcherProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 bg-white dark:bg-gray-900 shadow-xl w-64 py-1">
      <div className="px-3 py-2 border-b dark:border-gray-700">
        <p className="text-xs text-gray-400">Current organization</p>
        <p className="text-sm font-bold">{currentName}</p>
      </div>
      {orgs.map(o => (
        <button key={o.id} onClick={() => onSwitch(o.id)}
          className={`w-full text-left px-3 py-2 text-sm flex items-center justify-between ${
            o.active ? "bg-blue-50 dark:bg-blue-900/20" : "hover:bg-gray-50 dark:hover:bg-gray-800"
          }`}>
          <div>
            <span className="font-medium">{o.name}</span>
            <span className="text-xs text-gray-400 ml-1 capitalize">{o.plan}</span>
          </div>
          <span className="text-xs text-gray-400 capitalize">{o.role}</span>
        </button>
      ))}
      {canCreate && (
        <button onClick={onCreate}
          className="w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-gray-50 dark:hover:bg-gray-800 border-t dark:border-gray-700">
          + New Organization
        </button>
      )}
    </div>
  );
}
