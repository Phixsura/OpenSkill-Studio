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

import NewPathPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/paths/new/page";
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

describe("NewPathPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading and form fields", () => {
    render(<NewPathPage />, { wrapper: createWrapper() });
    expect(screen.getByText("New Learning Path")).toBeDefined();
    expect(screen.getByLabelText("Path name")).toBeDefined();
    expect(screen.getByLabelText("Description")).toBeDefined();
    expect(screen.getByLabelText("Estimated minutes")).toBeDefined();
    expect(screen.getByText("Create Learning Path")).toBeDefined();
  });

  it("allows filling in form fields", () => {
    render(<NewPathPage />, { wrapper: createWrapper() });
    const nameInput = screen.getByLabelText("Path name");
    fireEvent.change(nameInput, { target: { value: "My Path" } });
    expect((nameInput as HTMLInputElement).value).toBe("My Path");
  });

  it("submits form and calls API", async () => {
    mockApiWithAuth.mockResolvedValue({ data: { id: "new-path-1" } });
    render(<NewPathPage />, { wrapper: createWrapper() });

    fireEvent.change(screen.getByLabelText("Path name"), {
      target: { value: "Test Path" },
    });
    fireEvent.change(screen.getByLabelText("Description"), {
      target: { value: "A test learning path" },
    });

    fireEvent.click(screen.getByText("Create Learning Path"));

    await waitFor(() => {
      expect(mockApiWithAuth).toHaveBeenCalledWith(
        "/orgs/org-1/paths",
        expect.objectContaining({ method: "POST" }),
      );
    });
  });

  it("shows error message on submission failure", async () => {
    const err = new (ApiError as unknown as new (s: number, c: string, m: string) => Error)(
      422,
      "VALIDATION_ERROR",
      "Name already exists",
    );
    mockApiWithAuth.mockRejectedValue(err);
    render(<NewPathPage />, { wrapper: createWrapper() });

    fireEvent.change(screen.getByLabelText("Path name"), {
      target: { value: "Dup" },
    });
    fireEvent.click(screen.getByText("Create Learning Path"));

    expect(await screen.findByText("Name already exists")).toBeDefined();
  });

  it("shows Creating... while submitting", async () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<NewPathPage />, { wrapper: createWrapper() });

    fireEvent.change(screen.getByLabelText("Path name"), {
      target: { value: "Path" },
    });
    fireEvent.click(screen.getByText("Create Learning Path"));

    expect(await screen.findByText("Creating...")).toBeDefined();
  });
});
