import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const nav = vi.hoisted(() => ({ push: vi.fn(), replace: vi.fn() }));
vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "o-1", installId: "in-1" }),
  useRouter: () => ({ push: nav.push, replace: nav.replace }),
}));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/lib/api", () => {
  class MockApiError extends Error {
    constructor(
      public status: number,
      public code: string,
      message: string,
    ) {
      super(message);
    }
  }
  return { api: vi.fn(), apiWithAuth: vi.fn(), ApiError: MockApiError };
});

import WorkflowInstallationDetailPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/workflow-installations/[installId]/page";
import { api, apiWithAuth } from "@/lib/api";

const authApi = vi.mocked(apiWithAuth);
const pubApi = vi.mocked(api);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const INSTALL = {
  id: "in-1",
  pack_id: "pk-1",
  installed_version: "1.0.0",
  status: "active",
  locally_modified: false,
  installed_at: "2026-09-01T00:00:00Z",
  input_schema: [
    { key: "prompt", type: "text", label: "Prompt", required: true },
    { key: "params", type: "json", label: "Params", required: false },
  ],
};
const BINDINGS = [
  {
    id: "b-1",
    step_id: "st-gen",
    binding_mode: "preferred",
    offering_id: "off-suggested",
    reasons: [],
    gaps: [],
    confirmed_by: null,
  },
];
const OFFERINGS = [
  {
    id: "off-suggested",
    capability_key: "image_generation",
    model_name: "SDXL",
    quality_tier: "standard",
  },
  {
    id: "off-other",
    capability_key: "image_generation",
    model_name: "Flux",
    quality_tier: "premium",
  },
];

function route(reqs?: { path: string; method?: string; body?: unknown }[], install = INSTALL) {
  authApi.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method) {
      reqs?.push({
        path,
        method: init.method,
        body: init.body ? JSON.parse(init.body) : undefined,
      });
      if (path.endsWith("/workflow-runs")) return Promise.resolve({ data: { id: "run-9" } });
      return Promise.resolve({ data: { ok: true } });
    }
    if (path.endsWith("/bindings")) return Promise.resolve({ data: BINDINGS });
    if (path.endsWith("/provider-offerings")) return Promise.resolve({ data: OFFERINGS });
    if (path.includes("workflow-installations/in-1")) return Promise.resolve({ data: install });
    return Promise.resolve({ data: [] });
  }) as typeof apiWithAuth);
  pubApi.mockResolvedValue({ data: { name: "Render Pack", input_schema: [] } });
}

beforeEach(() => vi.clearAllMocks());

describe("WorkflowInstallationDetailPage (R499)", () => {
  it("confirming an untouched auto-suggested binding sends the SUGGESTED offering, not undefined", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(reqs);
    render(<WorkflowInstallationDetailPage />, { wrapper: wrapper() });
    await screen.findByText(/v1\.0\.0/);
    await screen.findByRole("button", { name: "Confirm" });
    fireEvent.click(screen.getByRole("button", { name: "Confirm" }));
    await waitFor(() => expect(reqs.some((r) => r.method === "PUT")).toBe(true));
    const put = reqs.find((r) => r.method === "PUT");
    expect(put?.path).toBe("/orgs/o-1/workflow-installations/in-1/bindings/st-gen");
    expect(put?.body).toEqual({ offering_id: "off-suggested", binding_mode: "preferred" });
  });

  it("edited binding sends the edited offering and mode", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(reqs);
    render(<WorkflowInstallationDetailPage />, { wrapper: wrapper() });
    await screen.findByRole("button", { name: "Confirm" });
    fireEvent.change(screen.getByLabelText("Offering for st-gen"), {
      target: { value: "off-other" },
    });
    fireEvent.change(screen.getByLabelText("Binding mode for st-gen"), {
      target: { value: "pinned" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Confirm" }));
    await waitFor(() => expect(reqs.some((r) => r.method === "PUT")).toBe(true));
    expect(reqs.find((r) => r.method === "PUT")?.body).toEqual({
      offering_id: "off-other",
      binding_mode: "pinned",
    });
  });

  it("json run inputs must parse to an object/array; blank json omitted; valid run posts and redirects", async () => {
    const reqs: { path: string; method?: string; body?: unknown }[] = [];
    route(reqs);
    render(<WorkflowInstallationDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Run Workflow");
    const jsonBox = screen.getByPlaceholderText('{"key": "value"}');
    fireEvent.change(jsonBox, { target: { value: "{bad" } });
    fireEvent.click(screen.getByRole("button", { name: "Start Run" }));
    expect(await screen.findByText("Enter valid JSON (object or array)")).toBeTruthy();
    expect(reqs.filter((r) => r.path.endsWith("/workflow-runs")).length).toBe(0);
    // scalar JSON is also rejected (backend needs dict/list)
    fireEvent.change(jsonBox, { target: { value: "42" } });
    fireEvent.click(screen.getByRole("button", { name: "Start Run" }));
    expect(await screen.findByText("Enter valid JSON (object or array)")).toBeTruthy();
    // blank json is omitted; text input carried through
    fireEvent.change(jsonBox, { target: { value: "" } });
    fireEvent.change(document.querySelector("#run-prompt") as HTMLElement, {
      target: { value: "a cat" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Start Run" }));
    await waitFor(() => expect(reqs.some((r) => r.path.endsWith("/workflow-runs"))).toBe(true));
    expect(reqs.find((r) => r.path.endsWith("/workflow-runs"))?.body).toEqual({
      installation_id: "in-1",
      inputs: { prompt: "a cat" },
    });
    await waitFor(() =>
      expect(nav.push).toHaveBeenCalledWith("/dashboard/orgs/o-1/workflow-runs/run-9"),
    );
  });

  it("fork and remove are confirm-gated; declined confirm sends nothing", async () => {
    const reqs: { path: string; method?: string }[] = [];
    route(reqs);
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValue(false);
    render(<WorkflowInstallationDetailPage />, { wrapper: wrapper() });
    await screen.findByRole("button", { name: /Fork \(Detach\)/ });
    fireEvent.click(screen.getByRole("button", { name: /Fork \(Detach\)/ }));
    fireEvent.click(screen.getByRole("button", { name: "Remove" }));
    expect(reqs.filter((r) => r.method === "POST" || r.method === "DELETE").length).toBe(0);
    confirmSpy.mockReturnValue(true);
    fireEvent.click(screen.getByRole("button", { name: /Fork \(Detach\)/ }));
    await waitFor(() => expect(reqs.some((r) => r.path.endsWith("/fork"))).toBe(true));
    confirmSpy.mockRestore();
  });
});
