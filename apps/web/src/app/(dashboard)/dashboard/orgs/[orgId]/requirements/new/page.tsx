"use client";

import { useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

const IO_TYPES = [
  "text",
  "prompt",
  "image",
  "video",
  "audio",
  "reference_asset",
  "json",
  "selection",
];

interface Capability {
  key: string;
  name: string;
}

interface Profile {
  id: string;
}

export default function NewRequirementPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const router = useRouter();
  const submitting = useRef(false);

  const [contextType, setContextType] = useState("learning");
  const [goal, setGoal] = useState("");
  const [scenario, setScenario] = useState("");
  const [outputType, setOutputType] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [timeBudget, setTimeBudget] = useState("");
  const [requiredCaps, setRequiredCaps] = useState<string[]>([]);
  const [preferredCaps, setPreferredCaps] = useState<string[]>([]);
  const [toolConstraints, setToolConstraints] = useState("");
  const [commercialUse, setCommercialUse] = useState(false);
  const [rawRequest, setRawRequest] = useState("");
  const [extractionUnavailable, setExtractionUnavailable] = useState(false);
  const [loading, setLoading] = useState(false);

  const { data: capsData } = useQuery({
    queryKey: ["capabilities"],
    queryFn: () => apiWithAuth<{ data: Capability[] }>("/capabilities"),
  });
  const capabilities = capsData?.data ?? [];

  const toggleCap = (
    key: string,
    list: string[],
    setList: (v: string[]) => void,
  ) => {
    setList(list.includes(key) ? list.filter((k) => k !== key) : [...list, key]);
  };

  const buildStructured = () => {
    const structured: Record<string, unknown> = {};
    if (goal.trim()) structured.goal = goal.trim();
    if (scenario.trim()) structured.scenario = scenario.trim();
    if (outputType) structured.output_type = outputType;
    if (difficulty) structured.difficulty = difficulty;
    if (timeBudget) structured.time_budget = parseInt(timeBudget, 10);
    if (requiredCaps.length) structured.required_capabilities = requiredCaps;
    if (preferredCaps.length) structured.preferred_capabilities = preferredCaps;
    if (toolConstraints.trim())
      structured.tool_constraints = toolConstraints
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
    if (commercialUse) structured.commercial_use = true;
    return structured;
  };

  const handleSubmit = async () => {
    if (submitting.current) return;
    submitting.current = true;
    setLoading(true);
    try {
      const res = await apiWithAuth<{ data: Profile }>(
        `/orgs/${orgId}/requirement-profiles`,
        {
          method: "POST",
          body: JSON.stringify({
            context_type: contextType,
            structured_requirements: buildStructured(),
            raw_request: rawRequest.trim() || null,
          }),
        },
      );
      toast.success("Requirement profile created");
      router.replace(`/dashboard/orgs/${orgId}/requirements/${res.data.id}`);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to create profile");
    } finally {
      submitting.current = false;
      setLoading(false);
    }
  };

  const handleExtract = async () => {
    if (submitting.current || !rawRequest.trim()) return;
    submitting.current = true;
    setLoading(true);
    try {
      const res = await apiWithAuth<{ data: Profile }>(
        `/orgs/${orgId}/requirement-profiles/extract`,
        {
          method: "POST",
          body: JSON.stringify({ context_type: contextType, raw_request: rawRequest }),
        },
      );
      toast.success("Requirements extracted — review before confirming");
      router.replace(`/dashboard/orgs/${orgId}/requirements/${res.data.id}`);
    } catch (err) {
      if (err instanceof ApiError && err.code === "EXTRACTION_DISABLED") {
        setExtractionUnavailable(true);
        toast.info("AI extraction is not enabled — use the guided form below");
      } else {
        toast.error(err instanceof ApiError ? err.message : "Extraction failed");
      }
    } finally {
      submitting.current = false;
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold">New Requirement</h1>
        <p className="mt-1 text-[hsl(var(--muted-foreground))]">
          Describe what you need — the matching engine works from this profile.
        </p>
      </div>

      <div className="space-y-2">
        <label htmlFor="context" className="text-sm font-medium">
          Context
        </label>
        <select
          id="context"
          value={contextType}
          onChange={(e) => setContextType(e.target.value)}
          className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
        >
          <option value="learning">Learning — compose a learning path</option>
          <option value="production">Production — compose a production solution</option>
          <option value="commercial_project">Commercial project</option>
          <option value="talent_matching">Talent matching</option>
        </select>
      </div>

      {/* Natural language extraction (feature-flagged server-side) */}
      {!extractionUnavailable && (
        <div className="space-y-2 rounded-lg border p-4">
          <label htmlFor="raw" className="text-sm font-medium">
            Describe in your own words (optional)
          </label>
          <textarea
            id="raw"
            value={rawRequest}
            onChange={(e) => setRawRequest(e.target.value)}
            maxLength={4000}
            rows={3}
            placeholder="e.g. 我想学习 AI 电商视觉制作，每周 5 小时，目标是能独立produce产品主图"
            className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
          />
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="secondary"
              onClick={handleExtract}
              disabled={loading || !rawRequest.trim()}
            >
              Extract with AI
            </Button>
            <span className="text-xs text-[hsl(var(--muted-foreground))]">
              Extracted fields stay editable — you confirm before matching.
            </span>
          </div>
        </div>
      )}
      {extractionUnavailable && (
        <p className="rounded-lg border border-dashed p-3 text-xs text-[hsl(var(--muted-foreground))]">
          AI extraction is not enabled on this server. Use the guided form.
        </p>
      )}

      <div className="space-y-4 rounded-lg border p-4">
        <h2 className="font-semibold">Guided form</h2>
        <div className="space-y-2">
          <label htmlFor="goal" className="text-sm font-medium">
            Goal
          </label>
          <Input
            id="goal"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="Learn AI e-commerce visual production"
            maxLength={500}
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <label htmlFor="scenario" className="text-sm font-medium">
              Scenario
            </label>
            <Input
              id="scenario"
              value={scenario}
              onChange={(e) => setScenario(e.target.value)}
              placeholder="ecommerce"
              maxLength={100}
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="output-type" className="text-sm font-medium">
              Output type
            </label>
            <select
              id="output-type"
              value={outputType}
              onChange={(e) => setOutputType(e.target.value)}
              className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
            >
              <option value="">(any)</option>
              {IO_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <label htmlFor="difficulty" className="text-sm font-medium">
              Current level
            </label>
            <select
              id="difficulty"
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
            >
              <option value="">(unspecified)</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
              <option value="expert">Expert</option>
            </select>
          </div>
          <div className="space-y-2">
            <label htmlFor="time-budget" className="text-sm font-medium">
              Time budget (minutes)
            </label>
            <Input
              id="time-budget"
              type="number"
              min={0}
              max={100000}
              value={timeBudget}
              onChange={(e) => setTimeBudget(e.target.value)}
              placeholder="1200"
            />
          </div>
        </div>

        <div className="space-y-2">
          <span className="text-sm font-medium">Required capabilities</span>
          <div className="flex flex-wrap gap-2">
            {capabilities.map((cap) => (
              <label
                key={cap.key}
                className="flex cursor-pointer items-center gap-1.5 rounded-full border px-3 py-1 text-xs"
              >
                <input
                  type="checkbox"
                  checked={requiredCaps.includes(cap.key)}
                  onChange={() => toggleCap(cap.key, requiredCaps, setRequiredCaps)}
                />
                {cap.name}
              </label>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <span className="text-sm font-medium">Preferred capabilities</span>
          <div className="flex flex-wrap gap-2">
            {capabilities.map((cap) => (
              <label
                key={cap.key}
                className="flex cursor-pointer items-center gap-1.5 rounded-full border px-3 py-1 text-xs"
              >
                <input
                  type="checkbox"
                  checked={preferredCaps.includes(cap.key)}
                  onChange={() => toggleCap(cap.key, preferredCaps, setPreferredCaps)}
                />
                {cap.name}
              </label>
            ))}
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <label htmlFor="tools" className="text-sm font-medium">
              Tool constraints (comma-separated)
            </label>
            <Input
              id="tools"
              value={toolConstraints}
              onChange={(e) => setToolConstraints(e.target.value)}
              placeholder="comfyui, midjourney"
            />
          </div>
          <label className="flex items-center gap-2 pt-6 text-sm">
            <input
              type="checkbox"
              checked={commercialUse}
              onChange={(e) => setCommercialUse(e.target.checked)}
            />
            Commercial use
          </label>
        </div>

        <Button onClick={handleSubmit} disabled={loading}>
          {loading ? "Creating..." : "Create Profile"}
        </Button>
      </div>
    </div>
  );
}
