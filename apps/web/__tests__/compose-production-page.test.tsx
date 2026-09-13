import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "o-1" }),
  useSearchParams: () => ({ get: () => null }),
}));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ProductionComposerPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/compose/production/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const PROFILE = {
  id: "prof-1",
  context_type: "production",
  status: "confirmed",
  structured_requirements: { goal: "Hero image" },
};

function draft(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    id: "d-1",
    status: "proposed",
    materialized_entity_id: null,
    payload: {
      workflow_chain: [
        { entity_id: "wf-2", name: "Upscale", order: 2 },
        { entity_id: "wf-1", name: "Generate", order: 1 },
      ],
      template: { entity_id: "t-1", name: "Visual Template" },
      items: [],
      placeholders: [],
      gaps: [],
      required_capabilities: [
        { capability: "image_gen", features: ["img2img"] },
        { capability: "image_gen", features: [] }, // same capability, distinct feature-set
      ],
      ...overrides,
    },
  };
}

function route(theDraft: unknown, opts?: { pages?: number }) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "POST") {
      if (path.endsWith("/confirm"))
        return Promise.resolve({
          data: {
            draft: { ...(theDraft as object), status: "confirmed", materialized_entity_id: "p-77" },
            materialized_entity_id: "p-77",
          },
        });
      return Promise.resolve({ data: theDraft });
    }
    if (path.includes("requirement-profiles")) {
      const page = Number(/page=(\d+)/.exec(path)?.[1] ?? "1");
      const pages = opts?.pages ?? 1;
      return Promise.resolve({
        data:
          page === pages
            ? [PROFILE]
            : [
                {
                  id: `draft-${page}`,
                  context_type: "production",
                  status: "draft",
                  structured_requirements: {},
                },
              ],
        meta: { has_more: page < pages },
      });
    }
    return Promise.resolve({ data: [] });
  }) as typeof apiWithAuth);
}

async function compose() {
  await waitFor(() => expect(screen.getByRole("option", { name: /Hero image/ })).toBeTruthy());
  fireEvent.change(screen.getByLabelText("Select confirmed profile"), {
    target: { value: "prof-1" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Compose Solution" }));
}

beforeEach(() => vi.clearAllMocks());

describe("ProductionComposerPage (R487)", () => {
  it("profile pagination follows has_more so page-2 confirmed profiles reach the select", async () => {
    route(draft(), { pages: 3 });
    render(<ProductionComposerPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByRole("option", { name: /Hero image/ })).toBeTruthy());
    const profileCalls = api.mock.calls
      .map((c) => String(c[0]))
      .filter((c) => c.includes("requirement-profiles"));
    expect(profileCalls.length).toBe(3); // followed has_more across pages
    // draft profiles from earlier pages are filtered out
    expect(screen.getAllByRole("option").length).toBe(2); // placeholder + confirmed
  });

  it("workflow chain renders sorted by order; duplicate-capability pills keyed by feature-set (R83/R84)", async () => {
    const d = draft({
      gaps: [
        { code: "NO_ELIGIBLE_PROVIDER", capability: "image_gen", missing_features: ["img2img"] },
      ],
    });
    route(d);
    render(<ProductionComposerPage />, { wrapper: wrapper() });
    await compose();
    await screen.findByText("Generate");
    // order 1 (“Generate”) renders before order 2 (“Upscale”) despite input order
    const body = document.body.textContent ?? "";
    expect(body.indexOf("Generate")).toBeLessThan(body.indexOf("Upscale"));
    // the (image_gen, img2img) pill is unmet; the bare image_gen pill is ready
    expect(screen.getByText(/image_gen \(img2img\) · no provider/)).toBeTruthy();
    expect(screen.getByText(/^image_gen · ready$/)).toBeTruthy();
    // gap banner text
    expect(screen.getByText(/No provider connected for "image_gen"/)).toBeTruthy();
  });

  it("missing template blocks Confirm; confirm flow shows the created-project link", async () => {
    const noTemplate = draft({ template: null });
    route(noTemplate);
    const first = render(<ProductionComposerPage />, { wrapper: wrapper() });
    await compose();
    await first.findByText(/No project template matched/);
    expect(
      (screen.getByRole("button", { name: /Confirm & Create Project/ }) as HTMLButtonElement)
        .disabled,
    ).toBe(true);
    first.unmount();

    vi.clearAllMocks();
    route(draft());
    render(<ProductionComposerPage />, { wrapper: wrapper() });
    await compose();
    await screen.findByText("Visual Template");
    const confirmBtn = screen.getByRole("button", { name: /Confirm & Create Project/ });
    expect((confirmBtn as HTMLButtonElement).disabled).toBe(false);
    fireEvent.click(confirmBtn);
    await screen.findByText("Project created.");
    expect(screen.getByText("Open the project →").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/projects/p-77",
    );
    // confirm section replaced by the success banner
    expect(screen.queryByRole("button", { name: /Confirm & Create Project/ })).toBeNull();
  });

  it("placeholder labels explain the reason; changing profile clears a stale draft", async () => {
    const d = draft({
      placeholders: [
        { input_key: "logo", type: "image", reason: "no_producer" },
        { input_key: "copy", type: "text", reason: "needs_user_value" },
      ],
    });
    route(d);
    render(<ProductionComposerPage />, { wrapper: wrapper() });
    await compose();
    await screen.findByText(/no workflow produces this/);
    expect(screen.getByText(/provided by you at run time/)).toBeTruthy();
    // switching profile resets the draft view
    fireEvent.change(screen.getByLabelText("Select confirmed profile"), {
      target: { value: "" },
    });
    expect(screen.queryByText("Visual Template")).toBeNull();
  });
});
