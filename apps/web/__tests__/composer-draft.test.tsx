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
  useParams: () => ({ orgId: "org-1" }),
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  useSearchParams: () => new URLSearchParams("profile=prof-1"),
}));

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import ComposeLearningPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/compose/learning/page";
import { apiWithAuth } from "@/lib/api";

const mockApiWithAuth = vi.mocked(apiWithAuth);

function createWrapper() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

const profiles = {
  data: [
    {
      id: "prof-1",
      org_id: "org-1",
      context_type: "learning",
      raw_request: null,
      structured_requirements: {
        goal: "Learn AI e-commerce visuals",
        time_budget: 1200,
        required_capabilities: ["image_generation"],
      },
      extraction_meta: { provenance: { goal: "user_entered" } },
      status: "confirmed",
      created_at: "2026-08-23T00:00:00Z",
    },
  ],
  meta: { total: 1, page: 1, per_page: 100, has_more: false },
};

describe("ComposeLearningPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders the heading and step sections", async () => {
    mockApiWithAuth.mockResolvedValue(profiles);
    render(<ComposeLearningPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Compose Learning Path")).toBeDefined();
    expect(screen.getByText("1. Requirement profile")).toBeDefined();
  });

  it("preselects the profile from the query param and shows its goal", async () => {
    mockApiWithAuth.mockResolvedValue(profiles);
    const { container } = render(<ComposeLearningPage />, {
      wrapper: createWrapper(),
    });
    await screen.findByText("Compose Learning Path");
    // Goal renders inside a <p> with sibling text nodes — assert on container text
    await vi.waitFor(() => {
      expect(container.textContent).toContain("Learn AI e-commerce visuals");
    });
  });

  it("only lists confirmed profiles in the selector", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        ...profiles.data,
        {
          ...profiles.data[0],
          id: "prof-2",
          status: "draft",
          structured_requirements: { goal: "Unconfirmed goal" },
        },
      ],
      meta: { total: 2, page: 1, per_page: 100, has_more: false },
    });
    const { container } = render(<ComposeLearningPage />, {
      wrapper: createWrapper(),
    });
    await screen.findByText("Compose Learning Path");
    const select = container.querySelector("select");
    expect(select).toBeDefined();
    const optionTexts = Array.from(select?.querySelectorAll("option") ?? []).map(
      (o) => o.textContent ?? "",
    );
    expect(optionTexts.join(" ")).not.toContain("Unconfirmed goal");
  });
});
