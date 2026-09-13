import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/lib/api", () => ({ api: vi.fn(), ApiError: class extends Error {} }));

import WorkflowRegistryPage from "@/app/registry/workflows/page";
import { api } from "@/lib/api";

const apiMock = vi.mocked(api);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const PACKS = [
  {
    id: "wp-1",
    name: "Render Pack",
    slug: "render",
    summary: "renders things",
    workflow_type: "comfyui",
    capability_tags: ["image_gen", "upscale", "inpaint", "extra"],
    install_count: 1,
    latest_version: "1.0.0",
    updated_at: "2026-09-01T00:00:00Z",
  },
];

function route(calls?: string[], packs: unknown[] = PACKS, hasMore = false) {
  apiMock.mockImplementation(((rawPath: unknown) => {
    calls?.push(String(rawPath ?? ""));
    return Promise.resolve({ data: packs, meta: { total: packs.length, has_more: hasMore } });
  }) as typeof api);
}

beforeEach(() => vi.clearAllMocks());
afterEach(() => vi.useRealTimers());

describe("WorkflowRegistryPage (R495)", () => {
  it("cards: type chip, first-3 capability tags only, singular install copy, detail link", async () => {
    route();
    render(<WorkflowRegistryPage />, { wrapper: wrapper() });
    await screen.findByText("Render Pack");
    expect(screen.getByText("comfyui")).toBeTruthy();
    expect(screen.getByText("image gen")).toBeTruthy(); // underscores humanized
    expect(screen.queryByText("extra")).toBeNull(); // sliced to 3 tags
    expect(document.body.textContent).toContain("1 install"); // singular
    expect(screen.getByText("Render Pack").closest("a")?.getAttribute("href")).toBe(
      "/registry/workflows/wp-1",
    );
  });

  it("search is debounced 300ms and filters combine; filter changes reset to page 1", async () => {
    vi.useFakeTimers();
    const calls: string[] = [];
    route(calls, PACKS, true);
    render(<WorkflowRegistryPage />, { wrapper: wrapper() });
    await act(async () => {
      await vi.runOnlyPendingTimersAsync();
    });
    // paginate to page 2 first
    fireEvent.click(screen.getByRole("button", { name: "Next" }));
    await act(async () => {
      await vi.runOnlyPendingTimersAsync();
    });
    expect(calls.some((c) => c.includes("page=2"))).toBe(true);
    // type a search: no request until the debounce elapses
    const before = calls.length;
    fireEvent.change(screen.getByLabelText("Search workflow packs"), {
      target: { value: "ren" },
    });
    await act(async () => {
      await vi.advanceTimersByTimeAsync(200);
    });
    expect(calls.length).toBe(before); // still within debounce
    await act(async () => {
      await vi.advanceTimersByTimeAsync(150);
    });
    await act(async () => {
      await vi.runOnlyPendingTimersAsync();
    });
    // the debounced search fired AND reset to page 1
    expect(calls.some((c) => c.includes("search=ren") && c.includes("page=1"))).toBe(true);
    // combine with capability filter
    await act(async () => {
      fireEvent.change(screen.getByLabelText("Capability"), { target: { value: "upscale" } });
      await vi.advanceTimersByTimeAsync(400);
    });
    expect(calls.some((c) => c.includes("search=ren") && c.includes("capability=upscale"))).toBe(
      true,
    );
  });

  it("empty + error states; pager hidden on single page", async () => {
    route(undefined, []);
    const first = render(<WorkflowRegistryPage />, { wrapper: wrapper() });
    expect(await first.findByText("No workflow packs found.")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Next" })).toBeNull();
    first.unmount();

    vi.clearAllMocks();
    apiMock.mockRejectedValue(new Error("down"));
    render(<WorkflowRegistryPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toMatch(/Failed|error/i));
  });
});
