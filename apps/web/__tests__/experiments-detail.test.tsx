import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/experiments/x",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useParams: () => ({ experimentId: "E".repeat(26) }),
}));
vi.mock("@/lib/use-me", () => ({ usePlatformAdmin: () => true }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ExperimentDetailPage from "@/app/(dashboard)/dashboard/experiments/[experimentId]/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function experiment(status: string, domain = "learning") {
  return {
    id: "E".repeat(26),
    key: "detail-exp",
    title: "Detail experiment",
    domain,
    scope_org_id: null,
    layer_key: "learning-core",
    status,
    current_version: 1,
    owner_user_id: "U".repeat(26),
    risk_class: "medium",
    ramp_bp: 5000,
    holdout_bp: 0,
    started_at: null,
    ended_at: null,
    analysis_close_at: null,
    start_at: null,
    last_guardrail_check_at: null,
    created_at: "2026-09-29T00:00:00Z",
    updated_at: "2026-09-29T00:00:00Z",
  };
}

function mockApiFor(status: string, domain = "learning") {
  api.mockImplementation(async (path: string) => {
    if (String(path).endsWith(`/experiments/${"E".repeat(26)}`)) {
      return { data: experiment(status, domain) };
    }
    if (String(path).endsWith("/analysis/latest")) return { data: null };
    return { data: [] };
  });
}

beforeEach(() => vi.clearAllMocks());

describe("Experiment detail lifecycle (ADR-017 Part L)", () => {
  it("review status renders the checklist incl. ethics for learning and sends it on schedule", async () => {
    mockApiFor("review");
    render(<ExperimentDetailPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Detail experiment")).toBeTruthy();
    const boxes = screen.getAllByRole("checkbox");
    expect(boxes.length).toBe(5); // 4 launch keys + ethics (learning domain)
    for (const box of boxes) fireEvent.click(box);
    fireEvent.click(screen.getByText("→ scheduled"));
    await waitFor(() =>
      expect(api.mock.calls.some((c) => String(c[0]).endsWith("/transition"))).toBe(true),
    );
    const call = api.mock.calls.find((c) => String(c[0]).endsWith("/transition"));
    const body = JSON.parse(String(call?.[1]?.body));
    expect(body.to_status).toBe("scheduled");
    expect(Object.values(body.checklist).every(Boolean)).toBe(true);
    expect(Object.keys(body.checklist).length).toBe(5);
  });

  it("non-ethics domains show only the four launch keys", async () => {
    mockApiFor("review", "marketplace");
    render(<ExperimentDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Detail experiment");
    expect(screen.getAllByRole("checkbox").length).toBe(4);
  });

  it("running status offers pause without a checklist body", async () => {
    mockApiFor("running");
    render(<ExperimentDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Detail experiment");
    expect(screen.queryByText(/Launch checklist/)).toBeNull();
    fireEvent.click(screen.getByText("→ paused"));
    await waitFor(() =>
      expect(api.mock.calls.some((c) => String(c[0]).endsWith("/transition"))).toBe(true),
    );
    const call = api.mock.calls.find((c) => String(c[0]).endsWith("/transition"));
    const body = JSON.parse(String(call?.[1]?.body));
    expect(body).toEqual({ to_status: "paused" });
  });

  it("sends start_at with the schedule transition when the field is set", async () => {
    mockApiFor("review");
    render(<ExperimentDetailPage />, { wrapper: wrapper() });
    const input = await screen.findByLabelText("Auto-start at");
    fireEvent.change(input, { target: { value: "2026-11-01T09:00" } });
    for (const key of await screen.findAllByRole("checkbox")) {
      fireEvent.click(key);
    }
    fireEvent.click(screen.getByText("→ scheduled"));
    await vi.waitFor(() => {
      const call = api.mock.calls.find((c) => String(c[0]).includes("/transition"));
      expect(call).toBeTruthy();
      const body = JSON.parse(String(call?.[1]?.body));
      expect(body.start_at).toContain("2026-11-01");
    });
  });

  it("renders the latest-analysis scorecard when a look exists", async () => {
    api.mockImplementation(((rawPath: unknown) => {
      const path = String(rawPath ?? "");
      if (path.endsWith("/analysis/latest"))
        return Promise.resolve({
          data: {
            at: "2026-10-02T12:00:00Z",
            sequential: "msprt",
            look: 3,
            result_hash: "a".repeat(64),
            automated: true,
            primary_effects: {
              exposure_rate: { treatment: { effect: 0.1234, se: 0.02 } },
            },
          },
        });
      if (/experiments\/E+$/.test(path)) return Promise.resolve({ data: experiment("running") });
      return Promise.resolve({ data: [] });
    }) as never);
    render(<ExperimentDetailPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/exposure_rate/)).toBeTruthy();
    expect(screen.getByText(/0.1234/)).toBeTruthy();
    expect(screen.getByText(/automated/)).toBeTruthy();
    expect(screen.getByText(/hash aaaaaaaaaaaa/)).toBeTruthy();
  });

  it("scheduled status shows the auto-start time or 'manual start'", async () => {
    mockApiFor("scheduled");
    render(<ExperimentDetailPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Auto-starts")).toBeTruthy();
    expect(screen.getByText("manual start")).toBeTruthy();
  });

  it("flags a running experiment whose guardrails were never checked", async () => {
    mockApiFor("running");
    render(<ExperimentDetailPage />, { wrapper: wrapper() });
    expect(await screen.findByText("never — sweep pending")).toBeTruthy();
  });

  it("analyzed status gates promote/reject behind the decision flow", async () => {
    mockApiFor("analyzed");
    render(<ExperimentDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Detail experiment");
    expect(screen.getByText(/recorded as a decision/)).toBeTruthy();
    expect(screen.queryByText("→ promoted")).toBeNull();
    expect(screen.queryByText("→ rejected")).toBeNull();
  });
});
