import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/experiments/new",
}));
vi.mock("@/lib/use-me", () => ({ usePlatformAdmin: () => true }));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  apiTextWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import { apiWithAuth } from "@/lib/api";
import { PlanningCalculator } from "@/app/(dashboard)/dashboard/experiments/components";

const apiMock = vi.mocked(apiWithAuth);

function wrap(ui: ReactNode) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

beforeEach(() => vi.clearAllMocks());

describe("PlanningCalculator (round 313, §4.13 planner)", () => {
  it("queries the planning endpoint and shows users-per-arm", async () => {
    apiMock.mockResolvedValue({
      data: { required_n_per_arm: 14744, degenerate: false },
    });
    wrap(<PlanningCalculator />);
    await waitFor(() =>
      expect(apiMock).toHaveBeenCalledWith(
        "/experiments/planning/sample-size?baseline_rate=0.1&mde_rel=0.1",
      ),
    );
    expect(await screen.findByText(/14,744 users per arm/)).toBeTruthy();
  });

  it("surfaces the degenerate flag honestly", async () => {
    apiMock.mockResolvedValue({
      data: { required_n_per_arm: null, degenerate: true },
    });
    wrap(<PlanningCalculator />);
    expect(await screen.findByText(/No detectable difference/)).toBeTruthy();
  });

  it("does not query on invalid local input", async () => {
    apiMock.mockResolvedValue({
      data: { required_n_per_arm: 1, degenerate: false },
    });
    wrap(<PlanningCalculator />);
    const baseline = screen.getByLabelText("baseline rate");
    fireEvent.change(baseline, { target: { value: "1.5" } });
    expect(await screen.findByText(/Enter a baseline in \(0,1\)/)).toBeTruthy();
    // only the initial valid default may have fired; never with 1.5
    for (const call of apiMock.mock.calls) {
      expect(String(call[0])).not.toContain("baseline_rate=1.5");
    }
  });
});
