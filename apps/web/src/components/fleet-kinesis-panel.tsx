"use client";
export function FleetKinesisPanel({ streams, active, shards, recordsPerSec }: { streams: number; active: number; shards: number; recordsPerSec: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌊 Kinesis</h3>
    <div className="text-sm">{active}/{streams} active · {shards} shards · {recordsPerSec.toLocaleString()} rec/s</div>
  </div>);
}
