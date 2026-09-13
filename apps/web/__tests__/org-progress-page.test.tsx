import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1" }) }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ProgressPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/progress/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const DATA = {
  skills_total: 8,
  skills_completed: 5,
  skills_in_progress: 2,
  exercises_total: 40,
  exercises_completed: 31,
  completion_percentage: 62.5,
  categories: [],
};

beforeEach(() => vi.clearAllMocks());

describe("ProgressPage (R498)", () => {
  it("stat cards render ratios and the progress bar width tracks the percentage", async () => {
    api.mockResolvedValue({ data: DATA });
    render(<ProgressPage />, { wrapper: wrapper() });
    await screen.findByText("My Progress");
    const body = document.body.textContent ?? "";
    expect(body).toContain("5/8"); // skills completed/total
    expect(body).toContain("31/40"); // exercises
    expect(screen.getAllByText("62.5%").length).toBe(2); // card + bar label
    const bar = document.querySelector(".bg-green-500") as HTMLElement;
    expect(bar.style.width).toBe("62.5%"); // width bound to the number, not a constant
  });

  it("fetch failure surfaces the error line; page hits the per-user endpoint", async () => {
    api.mockResolvedValue({ data: DATA });
    const first = render(<ProgressPage />, { wrapper: wrapper() });
    await first.findByText("My Progress");
    expect(api).toHaveBeenCalledWith("/orgs/o-1/progress/me");
    first.unmount();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("down"));
    render(<ProgressPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toContain("Failed to load progress"));
  });
});
