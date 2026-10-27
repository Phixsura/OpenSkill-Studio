"use client";
import { useState, useEffect } from "react";

interface RateLimitState {
  key: string;
  allowed: boolean;
  remaining: number;
  limit: number;
  retryAfter: number;
  violations: number;
  requestsLastMinute: number;
  requestsLastHour: number;
}

export function RateLimitVisualizer({ state, onReset }: {
  state: RateLimitState; onReset?: (key: string) => void;
}) {
  const fillPct = Math.round((state.remaining / state.limit) * 100);
  const penalized = state.violations > 0;
  const bucketColor = fillPct > 50 ? "bg-green-500" : fillPct > 20 ? "bg-yellow-500" : "bg-red-500";

  return (
    <div className="border dark:border-gray-700 rounded-xl p-4 space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <span className="font-bold text-sm">Rate Limit: {state.key}</span>
          {penalized && (
            <span className="ml-2 text-xs bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400 px-2 py-0.5 rounded-full">
              ⚠️ {state.violations} violation{state.violations > 1 ? "s" : ""} — {state.retryAfter}s cooldown
            </span>
          )}
        </div>
        <button onClick={() => onReset?.(state.key)} className="text-xs text-blue-500">Reset</button>
      </div>

      {/* Token bucket visualization */}
      <div>
        <div className="flex justify-between text-xs mb-1">
          <span>Token Bucket</span>
          <span className={state.remaining === 0 ? "text-red-500 font-bold" : ""}>
            {state.remaining}/{state.limit} tokens
          </span>
        </div>
        <div className="h-6 bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden relative">
          <div className={`h-full ${bucketColor} transition-all duration-300`}
            style={{ width: `${fillPct}%` }} />
          {/* Refill indicator */}
          <div className="absolute inset-0 flex items-center justify-center text-xs font-mono text-gray-600 dark:text-gray-300">
            {fillPct}%
          </div>
        </div>
      </div>

      {/* Request stats */}
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="border dark:border-gray-700 rounded-lg p-2">
          <span className={`text-lg font-bold block ${state.allowed ? "text-green-500" : "text-red-500"}`}>
            {state.allowed ? "✓" : "✕"}
          </span>
          <span className="text-[10px] text-gray-500">Last Request</span>
        </div>
        <div className="border dark:border-gray-700 rounded-lg p-2">
          <span className="text-lg font-bold block">{state.requestsLastMinute}</span>
          <span className="text-[10px] text-gray-500">Req/min</span>
        </div>
        <div className="border dark:border-gray-700 rounded-lg p-2">
          <span className="text-lg font-bold block">{state.requestsLastHour}</span>
          <span className="text-[10px] text-gray-500">Req/hour</span>
        </div>
      </div>

      {/* Penalty escalation indicator */}
      {state.violations > 0 && (
        <div className="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-lg p-2 text-xs">
          <span className="font-medium text-red-600">Penalty Level {state.violations}</span>
          <span className="text-red-500 ml-1">
            — backoff {Math.min(300, Math.pow(2, state.violations))}s
            {state.violations >= 3 && " (approaching max)"}
          </span>
        </div>
      )}
    </div>
  );
}
