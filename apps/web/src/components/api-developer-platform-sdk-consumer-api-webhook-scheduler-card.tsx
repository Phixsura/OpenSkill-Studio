"use client";

import { useState } from "react";

interface ScheduleInfo { id: string; eventType: string; frequency: string; enabled: boolean; executions: number; }

export default function WebhookSchedulerCard() {
  const [schedules] = useState<ScheduleInfo[]>([
    { id: "s1", eventType: "daily_report", frequency: "daily", enabled: true, executions: 30 },
    { id: "s2", eventType: "weekly_summary", frequency: "weekly", enabled: true, executions: 4 },
    { id: "s3", eventType: "health_check", frequency: "hourly", enabled: false, executions: 120 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Webhook Scheduler</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Scheduled webhook deliveries with cron</p>

      <div className="mt-4 space-y-2">
        {schedules.map((s) => (
          <div key={s.id} className={`flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700 ${!s.enabled ? "opacity-50" : ""}`}>
            <div className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${s.enabled ? "bg-green-500" : "bg-zinc-300"}`} />
              <span className="text-sm text-zinc-800 dark:text-zinc-200">{s.eventType}</span>
              <span className="rounded bg-zinc-100 px-1.5 py-0.5 text-xs text-zinc-500 dark:bg-zinc-800">{s.frequency}</span>
            </div>
            <span className="text-xs text-zinc-400">{s.executions} runs</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {schedules.filter((s) => s.enabled).length}/{schedules.length} active schedules
      </div>
    </div>
  );
}
