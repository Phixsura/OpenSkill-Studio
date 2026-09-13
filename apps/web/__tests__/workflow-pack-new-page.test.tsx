import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const nav = vi.hoisted(() => ({ replace: vi.fn() }));
vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "o-1" }),
  useRouter: () => ({ replace: nav.replace }),
}));
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
  return { apiWithAuth: vi.fn(), ApiError: MockApiError };
});

import NewWorkflowPackPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/workflow-packs/new/page";
import { apiWithAuth, ApiError } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function posted() {
  return JSON.parse((api.mock.calls[0]?.[1] as { body: string }).body);
}

beforeEach(() => vi.clearAllMocks());

describe("NewWorkflowPackPage (R497)", () => {
  it("minimal POST: blank optionals omitted, empty difficulty omitted, tags default []", async () => {
    api.mockResolvedValue({ data: { id: "wp-new" } });
    render(<NewWorkflowPackPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText("Workflow name"), { target: { value: "Hero Flow" } });
    fireEvent.click(screen.getByRole("button", { name: "Create Workflow Pack" }));
    await waitFor(() => expect(api).toHaveBeenCalled());
    expect(posted()).toEqual({
      name: "Hero Flow",
      workflow_type: "production",
      scenario_tags: [],
    });
    expect(nav.replace).toHaveBeenCalledWith("/dashboard/orgs/o-1/workflow-packs/wp-new");
  });

  it("full POST: type/difficulty selects honored, scenario tags trimmed + filtered", async () => {
    api.mockResolvedValue({ data: { id: "wp-new" } });
    render(<NewWorkflowPackPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText("Workflow name"), { target: { value: "Hero Flow" } });
    fireEvent.change(screen.getByLabelText("Summary"), { target: { value: "short" } });
    fireEvent.change(screen.getByLabelText("Description"), { target: { value: "long" } });
    fireEvent.change(screen.getByLabelText("Workflow type"), { target: { value: "pipeline" } });
    fireEvent.change(screen.getByLabelText("Difficulty"), { target: { value: "advanced" } });
    fireEvent.change(screen.getByLabelText("Scenario tags"), {
      target: { value: " ecommerce ,, product-photography " },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create Workflow Pack" }));
    await waitFor(() => expect(api).toHaveBeenCalled());
    expect(posted()).toEqual({
      name: "Hero Flow",
      summary: "short",
      description: "long",
      workflow_type: "pipeline",
      difficulty: "advanced",
      scenario_tags: ["ecommerce", "product-photography"],
    });
  });

  it("ApiError shown verbatim and no redirect", async () => {
    api.mockRejectedValue(new ApiError(409, "DUP", "Name already used"));
    render(<NewWorkflowPackPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText("Workflow name"), { target: { value: "Hero Flow" } });
    fireEvent.click(screen.getByRole("button", { name: "Create Workflow Pack" }));
    expect(await screen.findByText("Name already used")).toBeTruthy();
    expect(nav.replace).not.toHaveBeenCalled();
  });
});
