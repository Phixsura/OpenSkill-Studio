"use client";

import { toast } from "sonner";
import { useParams } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth } from "@/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

/* ---------- Interfaces ---------- */

interface PackDetail {
  id: string;
  name: string;
  slug: string;
  summary: string;
  description: string | null;
  status: string;
  visibility: string;
  install_count: number;
  difficulty: string;
  estimated_minutes: number | null;
  scenario_tags: string[];
  tool_tags: string[];
  learning_outcomes: string[];
  created_at: string;
}

interface PackSkill {
  pack_id: string;
  skill_id: string;
  skill_name: string;
  sort_order: number;
}

interface PackTemplate {
  pack_id: string;
  template_id: string;
  template_name: string;
  sort_order: number;
}

interface Release {
  id: string;
  version: string;
  component_count: number;
  changelog: string;
  checksum: string;
  released_at: string;
}

interface Skill {
  id: string;
  name: string;
}

interface Template {
  id: string;
  name: string;
}

interface DayCount {
  date: string;
  count: number;
}

interface PackAnalytics {
  install_count: number;
  average_rating: number | null;
  review_count: number;
  installs_by_version: { version: string; count: number }[];
  installs_by_day: DayCount[];
}

/* ---------- Color maps ---------- */

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  published: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  archived: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
};

const VISIBILITY_COLORS: Record<string, string> = {
  private: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
  public: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  unlisted: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
};

/* ---------- Component ---------- */

export default function PackDetailPage() {
  const { orgId, packId } = useParams<{ orgId: string; packId: string }>();
  const queryClient = useQueryClient();

  /* ---- Local state ---- */
  const [addSkillId, setAddSkillId] = useState("");
  const [addTemplateId, setAddTemplateId] = useState("");
  const [releaseVersion, setReleaseVersion] = useState("");
  const [releaseChangelog, setReleaseChangelog] = useState("");

  /* ---- Queries ---- */

  const { data: packData, isLoading, isError } = useQuery({
    queryKey: ["pack", orgId, packId],
    queryFn: () =>
      apiWithAuth<{ data: PackDetail }>(`/orgs/${orgId}/packs/${packId}`),
  });

  const { data: skillsData } = useQuery({
    queryKey: ["pack-skills", orgId, packId],
    queryFn: () =>
      apiWithAuth<{ data: PackSkill[] }>(
        `/orgs/${orgId}/packs/${packId}/skills`,
      ),
  });

  const { data: templatesData } = useQuery({
    queryKey: ["pack-templates", orgId, packId],
    queryFn: () =>
      apiWithAuth<{ data: PackTemplate[] }>(
        `/orgs/${orgId}/packs/${packId}/templates`,
      ),
  });

  const { data: releasesData } = useQuery({
    queryKey: ["pack-releases", orgId, packId],
    queryFn: () =>
      apiWithAuth<{ data: Release[] }>(
        `/orgs/${orgId}/packs/${packId}/releases`,
      ),
  });

  const { data: orgSkillsData } = useQuery({
    queryKey: ["skills", orgId],
    queryFn: () =>
      apiWithAuth<{ data: Skill[] }>(`/orgs/${orgId}/skills?per_page=100`),
  });

  const { data: orgTemplatesData } = useQuery({
    queryKey: ["project-templates", orgId],
    queryFn: () =>
      apiWithAuth<{ data: Template[] }>(`/orgs/${orgId}/project-templates`),
  });

  const { data: analyticsData } = useQuery({
    queryKey: ["pack-analytics", orgId, packId],
    queryFn: () =>
      apiWithAuth<{ data: PackAnalytics }>(
        `/orgs/${orgId}/packs/${packId}/analytics`,
      ),
  });

  const pack = packData?.data;
  const packSkills = skillsData?.data ?? [];
  const packTemplates = templatesData?.data ?? [];
  const releases = releasesData?.data ?? [];
  const orgSkills = orgSkillsData?.data ?? [];
  const orgTemplates = orgTemplatesData?.data ?? [];
  const analytics = analyticsData?.data;

  /* ---- Mutations ---- */

  const updatePackMutation = useMutation({
    mutationFn: (fields: Record<string, unknown>) =>
      apiWithAuth(`/orgs/${orgId}/packs/${packId}`, {
        method: "PUT",
        body: JSON.stringify(fields),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pack", orgId, packId] });
      queryClient.invalidateQueries({ queryKey: ["packs", orgId] });
      toast.success("Pack updated");
    },
    onError: (err: Error) =>
      toast.error(err.message || "Failed to update pack"),
  });

  const addSkillMutation = useMutation({
    mutationFn: (skillId: string) =>
      apiWithAuth(`/orgs/${orgId}/packs/${packId}/skills`, {
        method: "POST",
        body: JSON.stringify({ skill_id: skillId }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["pack-skills", orgId, packId],
      });
      setAddSkillId("");
      toast.success("Skill added");
    },
    onError: (err: Error) =>
      toast.error(err.message || "Failed to add skill"),
  });

  const removeSkillMutation = useMutation({
    mutationFn: (skillId: string) =>
      apiWithAuth(`/orgs/${orgId}/packs/${packId}/skills/${skillId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["pack-skills", orgId, packId],
      });
      toast.success("Skill removed");
    },
    onError: (err: Error) =>
      toast.error(err.message || "Failed to remove skill"),
  });

  const addTemplateMutation = useMutation({
    mutationFn: (templateId: string) =>
      apiWithAuth(`/orgs/${orgId}/packs/${packId}/templates`, {
        method: "POST",
        body: JSON.stringify({ template_id: templateId }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["pack-templates", orgId, packId],
      });
      setAddTemplateId("");
      toast.success("Template added");
    },
    onError: (err: Error) =>
      toast.error(err.message || "Failed to add template"),
  });

  const removeTemplateMutation = useMutation({
    mutationFn: (templateId: string) =>
      apiWithAuth(`/orgs/${orgId}/packs/${packId}/templates/${templateId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["pack-templates", orgId, packId],
      });
      toast.success("Template removed");
    },
    onError: (err: Error) =>
      toast.error(err.message || "Failed to remove template"),
  });

  const publishReleaseMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/packs/${packId}/releases`, {
        method: "POST",
        body: JSON.stringify({
          version: releaseVersion,
          changelog: releaseChangelog || undefined,
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["pack-releases", orgId, packId],
      });
      setReleaseVersion("");
      setReleaseChangelog("");
      toast.success("Release published");
    },
    onError: (err: Error) =>
      toast.error(err.message || "Failed to publish release"),
  });

  /* ---- Loading / error states ---- */

  if (isLoading) {
    return (
      <p className="text-[hsl(var(--muted-foreground))]">Loading...</p>
    );
  }
  if (isError || !pack) {
    return (
      <p className="text-[hsl(var(--destructive))]">
        Failed to load pack.
      </p>
    );
  }

  /* ---- Render ---- */

  return (
    <div className="space-y-8">
      {/* ===== Section 1: Pack Info ===== */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">{pack.name}</h1>
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[pack.status] ?? ""}`}
            >
              {pack.status}
            </span>
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${VISIBILITY_COLORS[pack.visibility] ?? ""}`}
            >
              {pack.visibility}
            </span>
          </div>
          {pack.summary && (
            <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
              {pack.summary}
            </p>
          )}
          <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
            {pack.install_count} install
            {pack.install_count !== 1 ? "s" : ""}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {pack.visibility !== "public" && (
            <Button
              size="sm"
              onClick={() => updatePackMutation.mutate({ visibility: "public" })}
              disabled={updatePackMutation.isPending}
            >
              Set Public
            </Button>
          )}
          {pack.visibility === "public" && (
            <Button
              size="sm"
              variant="outline"
              onClick={() =>
                updatePackMutation.mutate({ visibility: "private" })
              }
              disabled={updatePackMutation.isPending}
            >
              Set Private
            </Button>
          )}
          {pack.status !== "archived" && (
            <Button
              size="sm"
              variant="outline"
              className="text-red-600 hover:bg-red-50"
              onClick={() => {
                if (confirm("Archive this pack? This cannot be undone.")) {
                  updatePackMutation.mutate({ status: "archived" });
                }
              }}
              disabled={updatePackMutation.isPending}
            >
              Archive
            </Button>
          )}
        </div>
      </div>

      {/* ===== Section 2: Contents ===== */}
      <div className="space-y-6">
        <h2 className="text-xl font-semibold">Contents</h2>

        {/* --- Skills sub-list --- */}
        <div className="rounded-lg border p-4">
          <h3 className="text-sm font-semibold">Skills</h3>
          {packSkills.length === 0 ? (
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
              No skills added yet.
            </p>
          ) : (
            <ul className="mt-2 space-y-2">
              {packSkills.map((ps) => (
                <li
                  key={ps.skill_id}
                  className="flex items-center justify-between rounded border px-3 py-2 text-sm"
                >
                  <span>
                    {ps.skill_name}
                    <span className="ml-2 text-xs text-[hsl(var(--muted-foreground))]">
                      #{ps.sort_order}
                    </span>
                  </span>
                  <button
                    type="button"
                    className="text-red-600 hover:text-red-800"
                    onClick={() => removeSkillMutation.mutate(ps.skill_id)}
                    disabled={removeSkillMutation.isPending}
                    aria-label={`Remove skill ${ps.skill_name}`}
                  >
                    &times;
                  </button>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-3 flex gap-2">
            <select
              value={addSkillId}
              onChange={(e) => setAddSkillId(e.target.value)}
              className="flex-1 rounded-md border bg-transparent px-3 py-2 text-sm"
              aria-label="Select a skill to add"
            >
              <option value="">Select skill...</option>
              {orgSkills
                .filter(
                  (s) => !packSkills.some((ps) => ps.skill_id === s.id),
                )
                .map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
            </select>
            <Button
              size="sm"
              onClick={() => {
                if (addSkillId) addSkillMutation.mutate(addSkillId);
              }}
              disabled={!addSkillId || addSkillMutation.isPending}
            >
              Add
            </Button>
          </div>
        </div>

        {/* --- Templates sub-list --- */}
        <div className="rounded-lg border p-4">
          <h3 className="text-sm font-semibold">Templates</h3>
          {packTemplates.length === 0 ? (
            <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
              No templates added yet.
            </p>
          ) : (
            <ul className="mt-2 space-y-2">
              {packTemplates.map((pt) => (
                <li
                  key={pt.template_id}
                  className="flex items-center justify-between rounded border px-3 py-2 text-sm"
                >
                  <span>
                    {pt.template_name}
                    <span className="ml-2 text-xs text-[hsl(var(--muted-foreground))]">
                      #{pt.sort_order}
                    </span>
                  </span>
                  <button
                    type="button"
                    className="text-red-600 hover:text-red-800"
                    onClick={() =>
                      removeTemplateMutation.mutate(pt.template_id)
                    }
                    disabled={removeTemplateMutation.isPending}
                    aria-label={`Remove template ${pt.template_name}`}
                  >
                    &times;
                  </button>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-3 flex gap-2">
            <select
              value={addTemplateId}
              onChange={(e) => setAddTemplateId(e.target.value)}
              className="flex-1 rounded-md border bg-transparent px-3 py-2 text-sm"
              aria-label="Select a template to add"
            >
              <option value="">Select template...</option>
              {orgTemplates
                .filter(
                  (t) =>
                    !packTemplates.some((pt) => pt.template_id === t.id),
                )
                .map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
            </select>
            <Button
              size="sm"
              onClick={() => {
                if (addTemplateId)
                  addTemplateMutation.mutate(addTemplateId);
              }}
              disabled={!addTemplateId || addTemplateMutation.isPending}
            >
              Add
            </Button>
          </div>
        </div>
      </div>

      {/* ===== Section 3: Releases ===== */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Releases</h2>

        {releases.length === 0 ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            No releases yet.
          </p>
        ) : (
          <div className="space-y-3">
            {releases.map((rel) => (
              <div
                key={rel.id}
                className="flex items-center justify-between rounded-lg border p-4"
              >
                <div>
                  <span className="font-semibold">{rel.version}</span>
                  <span className="ml-2 text-xs text-[hsl(var(--muted-foreground))]">
                    {rel.component_count} component
                    {rel.component_count !== 1 ? "s" : ""}
                  </span>
                  {rel.changelog && (
                    <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                      {rel.changelog}
                    </p>
                  )}
                </div>
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  {new Date(rel.released_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="rounded-lg border p-4">
          <h3 className="text-sm font-semibold">Publish New Release</h3>
          <div className="mt-3 space-y-3">
            <div>
              <label
                htmlFor="releaseVersion"
                className="block text-sm font-medium"
              >
                Version
              </label>
              <Input
                id="releaseVersion"
                value={releaseVersion}
                onChange={(e) => setReleaseVersion(e.target.value)}
                placeholder="1.0.0"
                className="mt-1"
              />
            </div>
            <div>
              <label
                htmlFor="releaseChangelog"
                className="block text-sm font-medium"
              >
                Changelog
              </label>
              <textarea
                id="releaseChangelog"
                value={releaseChangelog}
                onChange={(e) => setReleaseChangelog(e.target.value)}
                rows={3}
                className="mt-1 block w-full rounded-md border bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
                placeholder="What changed in this release?"
              />
            </div>
            <Button
              onClick={() => publishReleaseMutation.mutate()}
              disabled={
                !releaseVersion.trim() || publishReleaseMutation.isPending
              }
            >
              {publishReleaseMutation.isPending
                ? "Publishing..."
                : "Publish"}
            </Button>
          </div>
        </div>
      </div>

      {/* ===== Section 4: Analytics ===== */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Analytics</h2>

        {!analytics ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Loading analytics...
          </p>
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-lg border p-4 text-center">
                <p className="text-3xl font-bold">
                  {analytics.install_count.toLocaleString()}
                </p>
                <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                  Total installs
                </p>
              </div>
              <div className="rounded-lg border p-4 text-center">
                <p className="text-3xl font-bold">
                  {analytics.average_rating != null
                    ? analytics.average_rating.toFixed(1)
                    : "--"}
                </p>
                <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                  Average rating
                </p>
              </div>
              <div className="rounded-lg border p-4 text-center">
                <p className="text-3xl font-bold">
                  {analytics.review_count.toLocaleString()}
                </p>
                <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
                  Reviews
                </p>
              </div>
            </div>

            {analytics.installs_by_version.length > 0 && (
              <div className="rounded-lg border p-4">
                <h3 className="text-sm font-semibold">Installs by Version</h3>
                <table className="mt-3 w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-[hsl(var(--muted-foreground))]">
                      <th className="pb-2 font-medium">Version</th>
                      <th className="pb-2 text-right font-medium">Installs</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analytics.installs_by_version.map((row) => (
                      <tr key={row.version} className="border-b last:border-0">
                        <td className="py-2">{row.version}</td>
                        <td className="py-2 text-right">
                          {row.count.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Installs by day — last 30 days bar chart */}
            {analytics.installs_by_day && analytics.installs_by_day.length > 0 && (
              <div className="rounded-lg border p-4">
                <h3 className="text-sm font-semibold">Installs — Last 30 Days</h3>
                <InstallsByDayChart data={analytics.installs_by_day} />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

/* ---------- Installs by Day Bar Chart ---------- */

function InstallsByDayChart({ data }: { data: DayCount[] }) {
  const maxCount = Math.max(...data.map((d) => d.count), 1);
  const firstDay = data[0];
  const lastDay = data[data.length - 1];

  return (
    <div className="mt-3">
      <div className="flex items-end gap-[2px]" style={{ height: 120 }}>
        {data.map((day) => {
          const heightPct = (day.count / maxCount) * 100;
          const barDate = new Date(day.date + "T00:00:00");
          const label = `${barDate.toLocaleDateString(undefined, { month: "short", day: "numeric" })}: ${day.count}`;
          return (
            <div
              key={day.date}
              className="group relative flex-1"
              style={{ height: "100%" }}
            >
              <div
                className="absolute bottom-0 w-full rounded-t bg-blue-500 transition-colors group-hover:bg-blue-400"
                style={{
                  height: `${Math.max(heightPct, day.count > 0 ? 2 : 0)}%`,
                  minHeight: day.count > 0 ? 2 : 0,
                }}
              />
              <div className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-1 hidden -translate-x-1/2 whitespace-nowrap rounded bg-[hsl(var(--popover))] px-2 py-1 text-xs text-[hsl(var(--popover-foreground))] shadow group-hover:block">
                {label}
              </div>
            </div>
          );
        })}
      </div>
      {firstDay && lastDay && (
        <div className="mt-1 flex justify-between text-[10px] text-[hsl(var(--muted-foreground))]">
          <span>
            {new Date(firstDay.date + "T00:00:00").toLocaleDateString(
              undefined,
              { month: "short", day: "numeric" },
            )}
          </span>
          <span>
            {new Date(lastDay.date + "T00:00:00").toLocaleDateString(
              undefined,
              { month: "short", day: "numeric" },
            )}
          </span>
        </div>
      )}
    </div>
  );
}
