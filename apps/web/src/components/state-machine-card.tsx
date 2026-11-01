"use client";

interface TransitionInfo {
  from_state: string;
  to_state: string;
  event: string;
}

interface EntityState {
  entity_id: string;
  current_state: string;
  transition_count: number;
}

interface StateMachineCardProps {
  machineId: string;
  states: string[];
  transitions: TransitionInfo[];
  entities: EntityState[];
  appName: string;
}

function StateBadge({ state, isCurrent }: { state: string; isCurrent: boolean }) {
  return (
    <span
      className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
        isCurrent
          ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
          : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
      }`}
    >
      {state}
    </span>
  );
}

export default function StateMachineCard({
  machineId,
  states,
  transitions,
  entities,
  appName,
}: StateMachineCardProps) {
  const stateDistribution = new Map<string, number>();
  for (const e of entities) {
    stateDistribution.set(e.current_state, (stateDistribution.get(e.current_state) ?? 0) + 1);
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">State Machine</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {appName} · {machineId}
          </p>
        </div>
        <span className="text-xs text-gray-400">{entities.length} entities</span>
      </div>

      {/* States */}
      <div className="mb-3">
        <p className="mb-1.5 text-xs font-medium text-gray-500">States</p>
        <div className="flex flex-wrap gap-1.5">
          {states.map((s) => {
            const count = stateDistribution.get(s) ?? 0;
            return (
              <span
                key={s}
                className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-[11px] dark:bg-gray-800"
              >
                <span className="text-gray-700 dark:text-gray-300">{s}</span>
                {count > 0 && <span className="text-blue-600 dark:text-blue-400">({count})</span>}
              </span>
            );
          })}
        </div>
      </div>

      {/* Transitions */}
      <div className="mb-3">
        <p className="mb-1.5 text-xs font-medium text-gray-500">Transitions</p>
        <div className="space-y-1">
          {transitions.map((t, i) => (
            <div key={i} className="flex items-center gap-1.5 text-[11px]">
              <span className="text-gray-600 dark:text-gray-400">{t.from_state}</span>
              <span className="text-gray-400">→</span>
              <span className="text-gray-600 dark:text-gray-400">{t.to_state}</span>
              <span className="rounded bg-purple-100 px-1 py-0.5 text-[9px] text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">
                {t.event}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Entities */}
      {entities.length > 0 && (
        <div className="border-t border-gray-100 pt-3 dark:border-gray-800">
          <p className="mb-1.5 text-xs font-medium text-gray-500">Entities</p>
          <div className="space-y-1">
            {entities.slice(0, 5).map((e) => (
              <div key={e.entity_id} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-gray-700 dark:text-gray-300">{e.entity_id}</span>
                  <StateBadge state={e.current_state} isCurrent />
                </div>
                <span className="text-[11px] text-gray-400">{e.transition_count} transitions</span>
              </div>
            ))}
            {entities.length > 5 && (
              <p className="text-center text-[11px] text-gray-400">+{entities.length - 5} more</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
