import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "org-1" }),
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/lib/api", () => {
  class MockApiError extends Error {
    status: number;
    code: string;
    constructor(status: number, code: string, message: string) {
      super(message);
      this.status = status;
      this.code = code;
      this.name = "ApiError";
    }
  }
  return {
    apiWithAuth: vi.fn(),
    ApiError: MockApiError,
  };
});

import NewPackPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/packs/new/page";
import { apiWithAuth, ApiError } from "@/lib/api";

const mockApiWithAuth = vi.mocked(apiWithAuth);

function createWrapper() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("NewPackPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading and form fields", () => {
    render(<NewPackPage />, { wrapper: createWrapper() });
    expect(screen.getByText("New Skill Pack")).toBeDefined();
    expect(screen.getByLabelText("Pack name")).toBeDefined();
    expect(screen.getByLabelText("Summary")).toBeDefined();
    expect(screen.getByLabelText("Description")).toBeDefined();
    expect(screen.getByLabelText("Visibility")).toBeDefined();
    expect(screen.getByLabelText("Difficulty")).toBeDefined();
    expect(screen.getByLabelText("Est. minutes")).toBeDefined();
    expect(screen.getByText("Create Skill Pack")).toBeDefined();
  });

  it("allows filling in form fields", () => {
    render(<NewPackPage />, { wrapper: createWrapper() });
    const nameInput = screen.getByLabelText("Pack name");
    fireEvent.change(nameInput, { target: { value: "My Pack" } });
    expect((nameInput as HTMLInputElement).value).toBe("My Pack");

    const summaryInput = screen.getByLabelText("Summary");
    fireEvent.change(summaryInput, { target: { value: "A summary" } });
    expect((summaryInput as HTMLInputElement).value).toBe("A summary");
  });

  it("submits form and calls API with correct data", async () => {
    mockApiWithAuth.mockResolvedValue({ data: { id: "new-pack-1" } });
    render(<NewPackPage />, { wrapper: createWrapper() });

    fireEvent.change(screen.getByLabelText("Pack name"), {
      target: { value: "Test Pack" },
    });
    fireEvent.change(screen.getByLabelText("Summary"), {
      target: { value: "Test summary" },
    });

    fireEvent.click(screen.getByText("Create Skill Pack"));

    await waitFor(() => {
      expect(mockApiWithAuth).toHaveBeenCalledWith(
        "/orgs/org-1/packs",
        expect.objectContaining({ method: "POST" }),
      );
    });
  });

  it("shows error message on submission failure", async () => {
    const err = new (ApiError as unknown as new (s: number, c: string, m: string) => Error)(
      422,
      "VALIDATION_ERROR",
      "Name is required",
    );
    mockApiWithAuth.mockRejectedValue(err);
    render(<NewPackPage />, { wrapper: createWrapper() });

    fireEvent.change(screen.getByLabelText("Pack name"), {
      target: { value: "X" },
    });
    fireEvent.click(screen.getByText("Create Skill Pack"));

    expect(await screen.findByText("Name is required")).toBeDefined();
  });

  it("shows button as Creating... while submitting", async () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<NewPackPage />, { wrapper: createWrapper() });

    fireEvent.change(screen.getByLabelText("Pack name"), {
      target: { value: "Pack" },
    });
    fireEvent.click(screen.getByText("Create Skill Pack"));

    expect(await screen.findByText("Creating...")).toBeDefined();
  });
});
