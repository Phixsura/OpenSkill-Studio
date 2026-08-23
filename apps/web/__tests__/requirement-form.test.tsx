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
}));

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {
    constructor(
      public status: number,
      public code: string,
      message: string,
    ) {
      super(message);
    }
  },
}));

import NewRequirementPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/requirements/new/page";
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

const capabilities = {
  data: [
    { key: "image_generation", name: "Image Generation", category: "generation", io_signature: {} },
    { key: "image_to_video", name: "Image to Video", category: "generation", io_signature: {} },
  ],
};

describe("NewRequirementPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading and goal input", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<NewRequirementPage />, { wrapper: createWrapper() });
    expect(screen.getByText("New Requirement")).toBeDefined();
    expect(document.getElementById("goal")).toBeDefined();
  });

  it("renders capability checkboxes from the capabilities catalog", async () => {
    mockApiWithAuth.mockResolvedValue(capabilities);
    render(<NewRequirementPage />, { wrapper: createWrapper() });
    expect((await screen.findAllByText("Image Generation")).length).toBeGreaterThan(0);
    expect(screen.getAllByText("Image to Video").length).toBeGreaterThan(0);
    // Checkboxes rendered (required + preferred groups both list capabilities)
    const checkboxes = screen.getAllByRole("checkbox");
    expect(checkboxes.length).toBeGreaterThanOrEqual(4);
  });

  it("renders the Extract with AI action", async () => {
    mockApiWithAuth.mockResolvedValue(capabilities);
    render(<NewRequirementPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Extract with AI")).toBeDefined();
  });
});
