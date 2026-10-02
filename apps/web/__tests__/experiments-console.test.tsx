import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const searchParams = { current: new URLSearchParams() };
const replace = vi.fn();

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/experiments",
  useRouter: () => ({ replace, push: vi.fn() }),
  useParams: () => ({ experimentId: "E".repeat(26) }),
  useSearchParams: () => searchParams.current,
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ExperimentsPage from "@/app/(dashboard)/dashboard/experiments/page";
import HoldoutsPage from "@/app/(dashboard)/dashboard/experiments/holdouts/page";
import PromotionsPage from "@/app/(dashboard)/dashboard/experiments/promotions/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const EXPERIMENT = {
  id: "E".repeat(26),
  key: "rubric-wording-b",
  title: "Rubric wording B",
  domain: "learning",
  scope_org_id: null,
  layer_key: "learning-core",
  status: "running",
  current_version: 1,
  owner_user_id: "U".repeat(26),
  risk_class: "medium",
  ramp_bp: 5000,
  holdout_bp: 0,
  started_at: "2026-09-30T00:00:00Z",
  ended_at: null,
  analysis_close_at: null,
  created_at: "2026-09-29T00:00:00Z",
};

beforeEach(() => {
  vi.clearAllMocks();
  searchParams.current = new URLSearchParams();
  api.mockResolvedValue({ data: [], meta: { total: 0, next_cursor: null } });
});

describe("Experiment Console list (ADR-017 Part L)", () => {
  it("renders experiments with status pill, ramp and totals", async () => {
    api.mockResolvedValue({ data: [EXPERIMENT], meta: { total: 1, next_cursor: null } });
    render(<ExperimentsPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Rubric wording B")).toBeTruthy();
    // "running" appears in the filter <option> AND as the row pill
    expect(screen.getAllByText("running").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("50%")).toBeTruthy();
    expect(screen.getByText("1 of 1")).toBeTruthy();
  });

  it("seeds filters from the URL and keeps them shareable", async () => {
    searchParams.current = new URLSearchParams("status=paused&domain=matching");
    render(<ExperimentsPage />, { wrapper: wrapper() });
    await waitFor(() => expect(api).toHaveBeenCalled());
    // Query carries both URL-seeded filters (R393 shareable-state law)
    const firstCallPath = String(api.mock.calls[0]?.[0] ?? "");
    expect(firstCallPath).toContain("status=paused");
    expect(firstCallPath).toContain("domain=matching");
    const statusSelect = screen.getByLabelText("Status filter") as HTMLSelectElement;
    expect(statusSelect.value).toBe("paused");
    // Changing a filter rewrites the URL
    fireEvent.change(statusSelect, { target: { value: "running" } });
    expect(replace).toHaveBeenCalledWith("/dashboard/experiments?status=running&domain=matching", {
      scroll: false,
    });
  });

  it("shows Load more when a next cursor exists", async () => {
    api.mockResolvedValue({
      data: [EXPERIMENT],
      meta: { total: 120, next_cursor: "01CURSOR" },
    });
    render(<ExperimentsPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Load more")).toBeTruthy();
    expect(screen.getByText("1 of 120")).toBeTruthy();
  });
});

describe("Promotions board", () => {
  it("offers approve/reject on drafts and apply on approved", async () => {
    api.mockResolvedValue({
      data: [
        {
          id: "D1".padEnd(26, "0"),
          decision_record_id: "R".repeat(26),
          target_type: "matching_config",
          target_ref: "M".repeat(26),
          status: "draft",
          applied_ref: null,
          apply_error: null,
          created_at: "2026-09-30T00:00:00Z",
        },
        {
          id: "D2".padEnd(26, "0"),
          decision_record_id: "R".repeat(26),
          target_type: "learning_path",
          target_ref: "L".repeat(26),
          status: "approved",
          applied_ref: null,
          apply_error: null,
          created_at: "2026-09-30T00:00:00Z",
        },
      ],
    });
    render(<PromotionsPage />, { wrapper: wrapper() });
    expect(await screen.findByText("matching_config")).toBeTruthy();
    expect(screen.getByText("Approve")).toBeTruthy();
    expect(screen.getByText("Reject")).toBeTruthy();
    expect(screen.getByText("Apply")).toBeTruthy();
  });
});

describe("Holdout groups page (ADR-017 §4.12 v2)", () => {
  const GROUP = {
    id: "H".repeat(26),
    key: "q4-learning-holdout",
    title: "Q4 learning holdout",
    domain: "learning",
    scope_org_id: null,
    holdout_bp: 500,
    status: "active",
    starts_at: "2026-10-01T00:00:00Z",
    ends_at: null,
  };

  it("lists groups with band percentage and release action", async () => {
    api.mockResolvedValue({ data: [GROUP] });
    render(<HoldoutsPage />, { wrapper: wrapper() });
    expect(await screen.findByText("q4-learning-holdout")).toBeTruthy();
    expect(screen.getByText("5.0%")).toBeTruthy();
    expect(screen.getByText("Release")).toBeTruthy();
  });

  it("creates a group with numeric holdout_bp and releases by id", async () => {
    api.mockResolvedValue({ data: [GROUP] });
    render(<HoldoutsPage />, { wrapper: wrapper() });
    await screen.findByText("q4-learning-holdout");
    fireEvent.change(screen.getByPlaceholderText("q4-learning-holdout"), {
      target: { value: "new-holdout" },
    });
    fireEvent.change(screen.getByPlaceholderText("Q4 learning holdout"), {
      target: { value: "New holdout" },
    });
    fireEvent.click(screen.getByText("Create"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/experiments/holdout-groups",
        expect.objectContaining({ method: "POST" }),
      ),
    );
    const createCall = api.mock.calls.find(
      (c) => c[0] === "/experiments/holdout-groups" && c[1]?.method === "POST",
    );
    const body = JSON.parse(String(createCall?.[1]?.body));
    expect(body).toEqual({
      key: "new-holdout",
      title: "New holdout",
      domain: "learning",
      holdout_bp: 500,
      scope_org_id: null,
      ends_at: null,
    });
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValue(false);
    fireEvent.click(screen.getByText("Release"));
    expect(api.mock.calls.some((c) => String(c[0]).includes("/release"))).toBe(false); // declined confirm = no release call
    confirmSpy.mockReturnValue(true);
    fireEvent.click(screen.getByText("Release"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        `/experiments/holdout-groups/${GROUP.id}/release`,
        expect.objectContaining({ method: "POST" }),
      ),
    );
    confirmSpy.mockRestore();
  });

  it("runs a holdout report and renders split, arms and the caveat", async () => {
    api.mockImplementation(async (path: string) => {
      if (String(path).includes("/report")) {
        return {
          data: {
            group_key: "q4-learning-holdout",
            metric_key: "project_approval_rate",
            window_days: 28,
            sampled_units: 1000,
            holdout_units: 48,
            general_units: 952,
            arms: {
              holdout: { numerator: 10, denominator: 48 },
              general: { numerator: 300, denominator: 952 },
            },
            comparison: { effect: 0.1, p: 0.1234 },
            caveat: "no single-feature causal claim.",
          },
        };
      }
      return { data: [GROUP] };
    });
    render(<HoldoutsPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Report"));
    expect(await screen.findByText(/48 held out/)).toBeTruthy();
    expect(screen.getByText(/p = 0.1234/)).toBeTruthy();
    expect(screen.getByText(/no single-feature causal claim/)).toBeTruthy();
  });

  it("released groups hide the release button", async () => {
    api.mockResolvedValue({
      data: [{ ...GROUP, status: "released", ends_at: "2026-12-01T00:00:00Z" }],
    });
    render(<HoldoutsPage />, { wrapper: wrapper() });
    expect(await screen.findByText("released")).toBeTruthy();
    expect(screen.queryByText("Release")).toBeNull();
  });
});
