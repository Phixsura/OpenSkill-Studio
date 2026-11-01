"use client";
export function FleetZeppelinPanel({ instances, running, notebooks, interpreters }: { instances: number; running: number; notebooks: number; interpreters: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📒 Zeppelin</h3>
    <div className="text-sm">{running}/{instances} running · {notebooks} notebooks · {interpreters} interpreters</div>
  </div>);
}
