"use client";

import { useParams } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

interface PathDetail {
  id: string;
  name: string;
  slug: string;
  description: string;
  status: string;
  estimated_minutes: number;
  created_at: string;
}

interface PathItem {
  id: string;
  item_type: "skill" | "project" | "section";
  skill_id?: string;
  project_id?: string;
  section_title?: string;
  sort_order: number;
  required: boolean;
}

interface SkillOption {
  id: string;
  name: string;
}

interface ProjectOption {
  id: string;
  title: string;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  published: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  archived: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
};

export default function PathDetailPage() {
  const { orgId, pathId } = useParams<{ orgId: string; pathId: string }>();
  const queryClient = useQueryClient();

  // ── Path data ──
  const { data: pathData, isLoading, isError } = useQuery({
    queryKey: ["path", orgId, pathId],
    queryFn: () =>
      apiWithAuth<{ data: PathDetail }>(`/orgs/${orgId}/paths/${pathId}`),
  });

  const path = pathData?.data;

  // ── Path items ──
  const { data: itemsData } = useQuery({
    queryKey: ["path-items", orgId, pathId],
    queryFn: () =>
      apiWithAuth<{ data: PathItem[] }>(
        `/orgs/${orgId}/paths/${pathId}/items`,
      ),
  });

  const items = itemsData?.data ?? [];
  const sortedItems = [...items].sort((a, b) => a.sort_order - b.sort_order);

  // ── Org skills & projects (for add item dropdowns) ──
  const { data: skillsData } = useQuery({
    queryKey: ["org-skills-options", orgId],
    queryFn: () =>
      apiWithAuth<{ data: SkillOption[] }>(`/orgs/${orgId}/skills`),
  });

  const { data: projectsData } = useQuery({
    queryKey: ["org-projects-options", orgId],
    queryFn: () =>
      apiWithAuth<{ data: ProjectOption[] }>(`/orgs/${orgId}/projects`),
  });

  const orgSkills = skillsData?.data ?? [];
  const orgProjects = projectsData?.data ?? [];

  // ── Editable name ──
  const [editName, setEditName] = useState("");
  const [synced, setSynced] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (path && !synced) {
      setEditName(path.name);
      setSynced(true);
    }
  }, [path, synced]);

  // ── Add item form state ──
  const [addType, setAddType] = useState<"skill" | "project" | "section">("skill");
  const [addSkillId, setAddSkillId] = useState("");
  const [addProjectId, setAddProjectId] = useState("");
  const [addSectionTitle, setAddSectionTitle] = useState("");
  const [addingItem, setAddingItem] = useState(false);
  const addSubmitting = useRef(false);

  // ── Helpers ──
  const skillNameMap = new Map(orgSkills.map((s) => [s.id, s.name]));
  const projectNameMap = new Map(orgProjects.map((p) => [p.id, p.title]));

  const handleUpdatePath = async (fields: Record<string, unknown>) => {
    setSaving(true);
    try {
      await apiWithAuth(`/orgs/${orgId}/paths/${pathId}`, {
        method: "PUT",
        body: JSON.stringify(fields),
      });
      queryClient.invalidateQueries({ queryKey: ["path", orgId, pathId] });
      queryClient.invalidateQueries({ queryKey: ["paths", orgId] });
      toast.success("Path updated.");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to update path.");
    } finally {
      setSaving(false);
    }
  };

  const handleSaveName = () => {
    if (editName.trim() && editName !== path?.name) {
      handleUpdatePath({ name: editName.trim() });
    }
  };

  const handlePublish = () => handleUpdatePath({ status: "published" });
  const handleArchive = () => handleUpdatePath({ status: "archived" });

  const handleAddItem = async () => {
    if (addSubmitting.current) return;
    addSubmitting.current = true;
    setAddingItem(true);

    const body: Record<string, unknown> = {
      item_type: addType,
      sort_order: sortedItems.length > 0
        ? (sortedItems[sortedItems.length - 1]?.sort_order ?? 0) + 1
        : 0,
    };

    if (addType === "skill") {
      if (!addSkillId) {
        setAddingItem(false);
        addSubmitting.current = false;
        return;
      }
      body.skill_id = addSkillId;
    } else if (addType === "project") {
      if (!addProjectId) {
        setAddingItem(false);
        addSubmitting.current = false;
        return;
      }
      body.project_id = addProjectId;
    } else {
      if (!addSectionTitle.trim()) {
        setAddingItem(false);
        addSubmitting.current = false;
        return;
      }
      body.section_title = addSectionTitle.trim();
    }

    try {
      await apiWithAuth(`/orgs/${orgId}/paths/${pathId}/items`, {
        method: "POST",
        body: JSON.stringify(body),
      });
      queryClient.invalidateQueries({ queryKey: ["path-items", orgId, pathId] });
      toast.success("Item added.");
      setAddSkillId("");
      setAddProjectId("");
      setAddSectionTitle("");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to add item.");
    } finally {
      setAddingItem(false);
      addSubmitting.current = false;
    }
  };

  const handleRemoveItem = async (itemId: string) => {
    try {
      await apiWithAuth(`/orgs/${orgId}/paths/${pathId}/items/${itemId}`, {
        method: "DELETE",
      });
      queryClient.invalidateQueries({ queryKey: ["path-items", orgId, pathId] });
      toast.success("Item removed.");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to remove item.");
    }
  };

  if (isLoading) return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  if (isError) return <p className="text-sm text-red-600">Failed to load path. Please try again.</p>;
  if (!path) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <Input
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              onBlur={handleSaveName}
              className="text-2xl font-bold"
            />
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[path.status] ?? ""}`}
            >
              {path.status}
            </span>
          </div>
          <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            {path.description}
          </p>
        </div>
        <div className="ml-4 flex items-center gap-2">
          {path.status === "draft" && (
            <Button size="sm" onClick={handlePublish} disabled={saving}>
              Publish
            </Button>
          )}
          {path.status !== "archived" && (
            <Button
              size="sm"
              variant="secondary"
              onClick={handleArchive}
              disabled={saving}
            >
              Archive
            </Button>
          )}
        </div>
      </div>

      {/* Items list */}
      <div>
        <h2 className="mb-3 text-lg font-semibold">Path Items</h2>
        {sortedItems.length === 0 && (
          <div className="rounded-lg border border-dashed p-12 text-center text-[hsl(var(--muted-foreground))]">
            No items yet. Add skills, projects, or sections below.
          </div>
        )}

        <div className="space-y-2">
          {sortedItems.map((item) => {
            if (item.item_type === "section") {
              return (
                <div
                  key={item.id}
                  className="flex items-center justify-between border-b pb-2 pt-4"
                >
                  <h3 className="text-sm font-bold uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
                    {item.section_title}
                  </h3>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleRemoveItem(item.id)}
                  >
                    Remove
                  </Button>
                </div>
              );
            }

            const itemName =
              item.item_type === "skill"
                ? skillNameMap.get(item.skill_id ?? "") ?? item.skill_id
                : projectNameMap.get(item.project_id ?? "") ?? item.project_id;

            return (
              <div
                key={item.id}
                className="flex items-center justify-between rounded-lg border px-4 py-3"
              >
                <div className="flex items-center gap-3">
                  <span className="rounded bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs capitalize">
                    {item.item_type}
                  </span>
                  <span className="text-sm font-medium">{itemName}</span>
                  {item.required && (
                    <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                      required
                    </span>
                  )}
                </div>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleRemoveItem(item.id)}
                >
                  Remove
                </Button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Add item form */}
      <div className="rounded-lg border p-4 space-y-3">
        <h3 className="font-medium">Add Item</h3>
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <label className="block text-sm font-medium">Type</label>
            <select
              value={addType}
              onChange={(e) =>
                setAddType(e.target.value as "skill" | "project" | "section")
              }
              className="mt-1 rounded-md border bg-transparent px-3 py-2 text-sm"
            >
              <option value="skill">Skill</option>
              <option value="project">Project</option>
              <option value="section">Section</option>
            </select>
          </div>

          {addType === "skill" && (
            <div className="flex-1">
              <label className="block text-sm font-medium">Skill</label>
              <select
                value={addSkillId}
                onChange={(e) => setAddSkillId(e.target.value)}
                className="mt-1 w-full rounded-md border bg-transparent px-3 py-2 text-sm"
              >
                <option value="">Select a skill...</option>
                {orgSkills.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {addType === "project" && (
            <div className="flex-1">
              <label className="block text-sm font-medium">Project</label>
              <select
                value={addProjectId}
                onChange={(e) => setAddProjectId(e.target.value)}
                className="mt-1 w-full rounded-md border bg-transparent px-3 py-2 text-sm"
              >
                <option value="">Select a project...</option>
                {orgProjects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.title}
                  </option>
                ))}
              </select>
            </div>
          )}

          {addType === "section" && (
            <div className="flex-1">
              <label className="block text-sm font-medium">Section title</label>
              <Input
                value={addSectionTitle}
                onChange={(e) => setAddSectionTitle(e.target.value)}
                placeholder="e.g. Week 1: Getting Started"
                className="mt-1"
              />
            </div>
          )}

          <Button
            onClick={handleAddItem}
            disabled={addingItem}
          >
            {addingItem ? "Adding..." : "Add Item"}
          </Button>
        </div>
      </div>
    </div>
  );
}
