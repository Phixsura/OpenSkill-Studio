import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("next/navigation", () => ({
  useParams: () => ({ packId: "pack-1" }),
}));

vi.mock("@/lib/api", () => ({
  api: vi.fn(),
  ApiError: class extends Error {},
}));

vi.mock("@/stores/auth", () => ({
  useAuthStore: { getState: () => ({ isAuthenticated: false }) },
}));

import RegistryPackDetailPage from "@/app/registry/[packId]/page";
import { api } from "@/lib/api";

const mockApi = vi.mocked(api);

const PACK_DETAIL = {
  id: "pack-1",
  name: "AI Prompt Engineering",
  slug: "ai-prompt",
  description: "A complete guide to prompt engineering.",
  summary: "Master prompt engineering",
  difficulty: "intermediate",
  estimated_minutes: 150,
  install_count: 87,
  language: "en",
  learning_outcomes: ["Write effective prompts", "Evaluate AI output"],
  scenario_tags: ["prompt-eng"],
  tool_tags: ["chatgpt"],
  capability_tags: ["writing"],
  provenance: {
    author_name: "Alice",
    license_name: "MIT",
    source_url: "https://example.com",
  },
  average_rating: 4.5,
  review_count: 12,
};

const RELEASES = [
  {
    id: "r1",
    version: "1.0.0",
    component_count: 5,
    changelog: "Initial release",
    released_at: "2026-03-01T00:00:00Z",
  },
];

const PREVIEW = {
  skills: [{ name: "Skill 1", description: "d", difficulty: "beginner", exercise_count: 3, prerequisites: [] }],
  templates: [{ name: "Template 1", description: "d", rubric_criteria_count: 2 }],
  categories: [{ name: "Cat 1" }],
  total_skills: 1,
  total_exercises: 3,
  total_templates: 1,
};

function mockAllApis(overrides?: { releases?: unknown[]; pack?: unknown }) {
  return (path: string) => {
    if (path.includes("/preview")) return Promise.resolve({ data: PREVIEW });
    if (path.includes("/releases")) return Promise.resolve({ data: overrides?.releases ?? RELEASES });
    return Promise.resolve({ data: overrides?.pack ?? PACK_DETAIL });
  };
}

function createWrapper() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("RegistryPackDetailPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows loading state", () => {
    mockApi.mockReturnValue(new Promise(() => {}));
    render(<RegistryPackDetailPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading...")).toBeDefined();
  });

  it("renders pack details when loaded", async () => {
    mockApi.mockImplementation(mockAllApis() as any);
    render(<RegistryPackDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("AI Prompt Engineering")).toBeDefined();
    expect(screen.getByText("by Alice")).toBeDefined();
    expect(screen.getByText("Master prompt engineering")).toBeDefined();
    expect(screen.getByText("intermediate")).toBeDefined();
    expect(screen.getByText("87 installs")).toBeDefined();
  });

  it("renders learning outcomes", async () => {
    mockApi.mockImplementation(mockAllApis() as any);
    render(<RegistryPackDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Write effective prompts")).toBeDefined();
    expect(screen.getByText("Evaluate AI output")).toBeDefined();
  });

  it("renders description section", async () => {
    mockApi.mockImplementation(mockAllApis() as any);
    render(<RegistryPackDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Description")).toBeDefined();
    expect(screen.getByText("A complete guide to prompt engineering.")).toBeDefined();
  });

  it("renders releases list", async () => {
    mockApi.mockImplementation(mockAllApis() as any);
    render(<RegistryPackDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("v1.0.0")).toBeDefined();
    expect(screen.getByText("5 components")).toBeDefined();
    expect(screen.getByText("Initial release")).toBeDefined();
  });

  it("shows error state on failure", async () => {
    mockApi.mockRejectedValue(new Error("fail"));
    render(<RegistryPackDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText(/Pack not found or failed to load/)).toBeDefined();
  });

  it("renders sidebar tags", async () => {
    mockApi.mockImplementation(mockAllApis() as any);
    render(<RegistryPackDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Scenarios")).toBeDefined();
    expect(screen.getByText("prompt-eng")).toBeDefined();
    expect(screen.getByText("Tools")).toBeDefined();
    expect(screen.getByText("chatgpt")).toBeDefined();
    expect(screen.getByText("Capabilities")).toBeDefined();
    expect(screen.getByText("writing")).toBeDefined();
  });

  it("renders license and estimated time", async () => {
    mockApi.mockImplementation(mockAllApis() as any);
    render(<RegistryPackDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("MIT")).toBeDefined();
    expect(screen.getByText("Estimated time")).toBeDefined();
    expect(screen.getByText("2h 30m")).toBeDefined();
  });
});
