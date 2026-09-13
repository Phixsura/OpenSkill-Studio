import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ packId: "wp-1" }) }));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/components/install-button", () => ({
  InstallButton: (props: { isAuthed: boolean }) => (
    <div data-testid="install-button" data-authed={String(props.isAuthed)} />
  ),
}));
vi.mock("@/components/marketplace-panel", () => ({ MarketplacePanel: () => <div /> }));
vi.mock("@/stores/auth", () => ({
  useAuthStore: {
    getState: () => ({ isAuthenticated: true }),
    subscribe: () => () => {},
  },
}));
vi.mock("@/lib/api", () => ({ api: vi.fn(), ApiError: class extends Error {} }));

import PublicWorkflowPackPage from "@/app/registry/workflows/[packId]/page";
import { api } from "@/lib/api";

const apiMock = vi.mocked(api);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const PACK = {
  id: "wp-1",
  name: "Render Pack",
  slug: "render",
  summary: "renders",
  description: "long about",
  workflow_type: "comfyui",
  capability_tags: ["image_generation"],
  install_count: 5,
  input_schema: [
    { key: "prompt", type: "text", required: true },
    { key: "seed", type: "number", required: false },
  ],
  output_schema: [{ key: "image", type: "image" }],
};
const PREVIEW = {
  version: "1.2.0",
  step_count: 2,
  definition: {
    steps: [
      { id: "st-1", name: "Generate", type: "provider_action" },
      { id: "st-2", name: "Upscale", type: "provider_action" },
    ],
  },
  requires_capabilities: [
    { capability: "image_generation", features: ["img2img"] },
    { capability: "image_generation", features: [] },
  ],
  recommended_packs: [{ family: "skill_pack", slug: "comp-101", version: "2.0.0" }],
};
const RELEASES = [
  {
    id: "rel-1",
    version: "1.2.0",
    step_count: 2,
    released_at: "2026-09-01T00:00:00Z",
    checksum: "abcdef1234567890deadbeef",
    changelog: "Adds upscale",
  },
];

function route(opts?: { previewFails?: boolean }) {
  apiMock.mockImplementation(((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    if (path.endsWith("/releases")) return Promise.resolve({ data: RELEASES });
    if (path.endsWith("/preview"))
      return opts?.previewFails
        ? Promise.reject(new Error("403"))
        : Promise.resolve({ data: PREVIEW });
    return Promise.resolve({ data: PACK });
  }) as typeof api);
}

beforeEach(() => vi.clearAllMocks());

describe("PublicWorkflowPackPage (R496)", () => {
  it("typed I/O: required marker only on required inputs; outputs listed", async () => {
    route();
    render(<PublicWorkflowPackPage />, { wrapper: wrapper() });
    await screen.findByText("Render Pack");
    const promptRow = screen.getByText("prompt").closest("li");
    expect(promptRow?.textContent).toContain("required");
    const seedRow = screen.getByText("seed").closest("li");
    expect(seedRow?.textContent).not.toContain("required"); // required:false
    const outCode = screen.getAllByText("image").find((el) => el.tagName === "CODE");
    expect(outCode).toBeTruthy();
  });

  it("structure preview + duplicate-capability badges keyed by feature-set (R83/R84) + version history", async () => {
    route();
    render(<PublicWorkflowPackPage />, { wrapper: wrapper() });
    await screen.findByText("Render Pack");
    await screen.findByText(/Workflow structure \(2 steps · v1\.2\.0\)/);
    expect(screen.getByText("Generate")).toBeTruthy();
    // BOTH image_generation badges render (feature-set key, not capability key)
    expect(screen.getByText("image generation (img2img)")).toBeTruthy();
    // the bare capability badge + the pack tag chip both say "image generation"
    expect(screen.getAllByText("image generation").length).toBe(2);
    // recommended pack line
    expect(screen.getByText(/comp-101 \(skill pack 2\.0\.0\)/)).toBeTruthy();
    // release row: truncated checksum + changelog
    expect(screen.getByText("abcdef123456")).toBeTruthy();
    expect(screen.queryByText("abcdef1234567890deadbeef")).toBeNull();
    expect(screen.getByText("Adds upscale")).toBeTruthy();
    // install button knows auth state
    expect(screen.getByTestId("install-button").getAttribute("data-authed")).toBe("true");
  });

  it("preview 403 (unpublished/private) degrades gracefully — pack still renders, no structure section", async () => {
    route({ previewFails: true });
    render(<PublicWorkflowPackPage />, { wrapper: wrapper() });
    await screen.findByText("Render Pack");
    await screen.findByText("Adds upscale"); // releases still load
    expect(screen.queryByText(/Workflow structure/)).toBeNull();
    expect(screen.queryByText("Dependencies")).toBeNull();
  });

  it("missing pack renders not-found with a registry backlink", async () => {
    apiMock.mockRejectedValue(new Error("404"));
    render(<PublicWorkflowPackPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText("Workflow pack not found.")).toBeTruthy());
    expect(screen.getByText("← Back to registry").closest("a")?.getAttribute("href")).toBe(
      "/registry/workflows",
    );
  });
});
