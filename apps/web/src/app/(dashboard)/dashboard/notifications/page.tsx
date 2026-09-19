"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Notification {
  id: string;
  event_type: string;
  title: string;
  message: string;
  metadata: Record<string, unknown>;
  read_at: string | null;
  created_at: string;
}

interface NotificationPreference {
  event_type: string;
  channel: string;
  enabled: boolean;
}

const EVENT_TYPE_ICONS: Record<string, string> = {
  application_status_changed: "📋",
  new_match_found: "🎯",
  outreach_received: "💌",
  credential_issued: "🏆",
  interview_scheduled: "📅",
  offer_extended: "🎉",
  endorsement_received: "👍",
  pool_invitation: "👥",
  passport_viewed: "👁",
};

const EVENT_TYPE_LABELS: Record<string, string> = {
  application_status_changed: "Application Status Changes",
  new_match_found: "New Match Opportunities",
  outreach_received: "Outreach Received",
  credential_issued: "Credential Issued",
  interview_scheduled: "Interview Scheduled",
  offer_extended: "Offer Extended",
  endorsement_received: "Endorsement Received",
  pool_invitation: "Pool Invitation",
  passport_viewed: "Passport Viewed",
};

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  return new Date(dateStr).toLocaleDateString();
}

export default function NotificationsPage() {
  const [tab, setTab] = useState<"all" | "settings">("all");
  const queryClient = useQueryClient();

  // Notifications list
  const { data: notifData, isLoading: notifLoading } = useQuery({
    queryKey: ["talent-notifications"],
    queryFn: () =>
      api<{ data: Notification[]; meta: { next_cursor: string | null; has_more: boolean } }>(
        "/talent/notifications?limit=50",
      ),
    enabled: tab === "all",
  });

  // Unread count
  const { data: unreadData } = useQuery({
    queryKey: ["talent-notifications-unread"],
    queryFn: () => api<{ data: { unread_count: number } }>("/talent/notifications/unread-count"),
  });

  // Preferences
  const { data: prefData, isLoading: prefLoading } = useQuery({
    queryKey: ["talent-notification-preferences"],
    queryFn: () => api<{ data: NotificationPreference[] }>("/talent/notifications/preferences"),
    enabled: tab === "settings",
  });

  // Mark one read
  const markRead = useMutation({
    mutationFn: (id: string) => api(`/talent/notifications/${id}/read`, { method: "PATCH" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["talent-notifications"] });
      queryClient.invalidateQueries({ queryKey: ["talent-notifications-unread"] });
    },
  });

  // Mark all read
  const markAllRead = useMutation({
    mutationFn: () => api("/talent/notifications/mark-all-read", { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["talent-notifications"] });
      queryClient.invalidateQueries({ queryKey: ["talent-notifications-unread"] });
    },
  });

  // Update preferences
  const updatePrefs = useMutation({
    mutationFn: (preferences: { event_type: string; enabled: boolean }[]) =>
      api("/talent/notifications/preferences", {
        method: "PUT",
        body: JSON.stringify({ preferences }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["talent-notification-preferences"] });
    },
  });

  const notifications = notifData?.data ?? [];
  const unreadCount = unreadData?.data?.unread_count ?? 0;
  const preferences = prefData?.data ?? [];

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold">Notifications</h1>
          {unreadCount > 0 && (
            <span className="rounded-full bg-[hsl(var(--primary))] px-2.5 py-0.5 text-xs font-semibold text-[hsl(var(--primary-foreground))]">
              {unreadCount}
            </span>
          )}
        </div>
        {tab === "all" && unreadCount > 0 && (
          <button
            onClick={() => markAllRead.mutate()}
            disabled={markAllRead.isPending}
            className="rounded-md border px-3 py-1.5 text-sm hover:bg-[hsl(var(--secondary))]"
          >
            Mark all as read
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-lg border bg-[hsl(var(--secondary))] p-1">
        <button
          onClick={() => setTab("all")}
          className={cn(
            "flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors",
            tab === "all"
              ? "bg-[hsl(var(--card))] shadow-sm"
              : "text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]",
          )}
        >
          All Notifications
        </button>
        <button
          onClick={() => setTab("settings")}
          className={cn(
            "flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors",
            tab === "settings"
              ? "bg-[hsl(var(--card))] shadow-sm"
              : "text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]",
          )}
        >
          Settings
        </button>
      </div>

      {/* All Notifications Tab */}
      {tab === "all" && (
        <div className="space-y-2">
          {notifLoading && (
            <div className="py-12 text-center text-[hsl(var(--muted-foreground))]">
              Loading notifications…
            </div>
          )}
          {!notifLoading && notifications.length === 0 && (
            <div className="rounded-lg border bg-[hsl(var(--card))] p-12 text-center">
              <div className="mb-3 text-4xl">🔔</div>
              <h2 className="text-lg font-semibold">No notifications yet</h2>
              <p className="mt-1 text-[hsl(var(--muted-foreground))]">
                You&apos;ll see updates here when something happens.
              </p>
            </div>
          )}
          {notifications.map((n) => (
            <button
              key={n.id}
              onClick={() => !n.read_at && markRead.mutate(n.id)}
              className={cn(
                "flex w-full items-start gap-3 rounded-lg border p-4 text-left transition-colors",
                n.read_at
                  ? "bg-[hsl(var(--card))]"
                  : "border-[hsl(var(--primary))]/30 bg-[hsl(var(--primary))]/5",
              )}
            >
              <span className="mt-0.5 text-xl">{EVENT_TYPE_ICONS[n.event_type] ?? "📢"}</span>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-medium">{n.title}</p>
                  {!n.read_at && <span className="h-2 w-2 rounded-full bg-[hsl(var(--primary))]" />}
                </div>
                <p className="mt-0.5 text-sm text-[hsl(var(--muted-foreground))]">{n.message}</p>
                <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
                  {timeAgo(n.created_at)}
                </p>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Settings Tab */}
      {tab === "settings" && (
        <div className="rounded-lg border bg-[hsl(var(--card))] p-6">
          <h2 className="mb-4 text-lg font-semibold">Notification Preferences</h2>
          <p className="mb-6 text-sm text-[hsl(var(--muted-foreground))]">
            Choose which notifications you want to receive.
          </p>
          {prefLoading && (
            <div className="py-8 text-center text-[hsl(var(--muted-foreground))]">
              Loading preferences…
            </div>
          )}
          <div className="space-y-4">
            {Object.entries(EVENT_TYPE_LABELS).map(([eventType, label]) => {
              const pref = preferences.find((p) => p.event_type === eventType);
              const enabled = pref?.enabled ?? true;
              return (
                <label
                  key={eventType}
                  className="flex items-center justify-between rounded-md border px-4 py-3"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{EVENT_TYPE_ICONS[eventType] ?? "📢"}</span>
                    <span className="text-sm font-medium">{label}</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={enabled}
                    onChange={() => {
                      updatePrefs.mutate([{ event_type: eventType, enabled: !enabled }]);
                    }}
                    className="h-5 w-5 rounded border-gray-300"
                  />
                </label>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
