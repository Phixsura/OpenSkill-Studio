"use client";

interface Org { id: string; name: string; initials: string; role: string; plan: string; isCurrent: boolean; }
interface OrgSwitcherProps { orgs: Org[]; current: Org | null; canCreate: boolean;
  onSwitch: (id: string) => void; onCreate: () => void; }

export function OrgSwitcher({ orgs, current, canCreate, onSwitch, onCreate }: OrgSwitcherProps) {
  return (
    <div className="w-64 rounded-xl border bg-white shadow-xl dark:bg-gray-900 dark:border-gray-700">
      {current && (
        <div className="border-b px-4 py-3 dark:border-gray-700">
          <p className="text-xs text-gray-400">Current</p>
          <p className="text-sm font-semibold">{current.name}</p>
          <p className="text-xs text-gray-400">{current.role} · {current.plan}</p>
        </div>
      )}
      <div className="py-1">
        {orgs.filter(o => !o.isCurrent).map(o => (
          <button key={o.id} onClick={() => onSwitch(o.id)}
            className="flex w-full items-center gap-3 px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gray-200 text-xs font-bold dark:bg-gray-700">{o.initials}</div>
            <div className="text-left">
              <p className="font-medium">{o.name}</p>
              <p className="text-xs text-gray-400">{o.role}</p>
            </div>
          </button>
        ))}
      </div>
      {canCreate && (
        <div className="border-t px-4 py-2 dark:border-gray-700">
          <button onClick={onCreate} className="w-full text-left text-sm text-blue-600 hover:underline">+ Create Organization</button>
        </div>
      )}
    </div>
  );
}
