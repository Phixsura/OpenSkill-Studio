"use client";
export function FleetApiMigrationGuideV9Panel({ migrations, completed }: { migrations: number; completed: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Migration Guide v9</h3>
    <div className="text-sm">{migrations} migrations · {completed} completed</div>
  </div>);
}
