import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import OpportunityMatchesPage from "@/app/(dashboard)/dashboard/opportunities/matches/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

beforeEach(() => vi.clearAllMocks());

describe("OpportunityMatchesPage (R583)", () => {
  it("renders the backend TalentMatchResult shape (entity_id/display_name/score)", async () => {
    // The API returns this exact shape; the page previously read
    // opportunity_id/title/match_score and rendered empty title + NaN%.
    api.mockResolvedValue({
      data: [
        {
          entity_id: "OPP1",
          entity_type: "opportunity",
          display_name: "Senior AI Designer",
          score: 0.82,
          tier: "great",
          reasons: [{ code: "CAPABILITY_GAP_SCORE", label: "Meets capability requirements" }],
          gaps: [{ code: "PORTFOLIO_RELEVANCE", label: "Relevant project portfolio" }],
        },
      ],
    });
    render(<OpportunityMatchesPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Senior AI Designer")).toBeTruthy();
    expect(screen.getByText("82%")).toBeTruthy(); // score, not NaN
    expect(screen.getByText("great")).toBeTruthy();
    expect(screen.getByText("✓ Meets capability requirements")).toBeTruthy();
    expect(screen.getByText("△ Relevant project portfolio")).toBeTruthy();
    // detail link uses entity_id
    const link = screen.getByText("View & Apply").closest("a");
    expect(link?.getAttribute("href")).toBe("/dashboard/opportunities/OPP1");
  });

  it("shows the empty state when there are no matches", async () => {
    api.mockResolvedValue({ data: [] });
    render(<OpportunityMatchesPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText("No Matches Yet")).toBeTruthy());
  });
});
