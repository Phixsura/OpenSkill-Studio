import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/ecosystem/review",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import BlindReviewPage from "@/app/(dashboard)/dashboard/ecosystem/review/page";
import { ApiError, apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);
const ApiErrorCtor = ApiError as unknown as new (message: string) => Error;

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const BATCH = "B".repeat(26);
const REVIEW = "R".repeat(26);

beforeEach(() => {
  vi.clearAllMocks();
  api.mockImplementation((path: string, init?: RequestInit) => {
    if (path === `/ecosystem/benchmark/review-batches/${BATCH}/assignments` && !init)
      return Promise.resolve({
        data: [
          {
            review_id: REVIEW,
            alias_label: "Model A",
            output_assets: [{ kind: "text", ref: "out.txt" }],
            input_snapshot: { prompt: "draw a cat" },
            submitted: false,
            scores: {},
          },
        ],
      });
    return Promise.resolve({ data: {} });
  });
});

async function loadBatch() {
  render(<BlindReviewPage />, { wrapper: wrapper() });
  fireEvent.change(screen.getByPlaceholderText("Review batch ID"), {
    target: { value: BATCH },
  });
  fireEvent.click(screen.getByText("Load assignments"));
  expect(await screen.findByText("Model A")).toBeDefined();
}

describe("Blind review submit + reveal (ADR-016 §17 UI)", () => {
  it("assignments stay aliased — no model identity shown before reveal", async () => {
    await loadBatch();
    // Alias only; nothing that looks like an entity id or provider name
    expect(screen.getByText("Model A")).toBeDefined();
    expect(screen.queryByText(/entity_id/)).toBeNull();
  });

  it("Submit scores POSTs the per-dimension scores for that review", async () => {
    await loadBatch();
    const inputs = screen.getAllByRole("spinbutton");
    fireEvent.change(inputs[0]!, { target: { value: "4.5" } });
    fireEvent.click(screen.getByText("Submit scores"));
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) =>
        c[0] === `/ecosystem/benchmark/reviews/${REVIEW}/submit` &&
        (c[1] as RequestInit)?.method === "POST",
    );
    expect(call).toBeDefined();
    const body = JSON.parse((call![1] as RequestInit).body as string);
    expect(body.scores.quality).toBe(4.5);
  });

  it("premature reveal surfaces the API refusal instead of identities", async () => {
    api.mockImplementation((path: string, init?: RequestInit) => {
      if (path === `/ecosystem/benchmark/review-batches/${BATCH}/assignments` && !init)
        return Promise.resolve({
          data: [
            {
              review_id: REVIEW,
              alias_label: "Model A",
              output_assets: [],
              input_snapshot: {},
              submitted: false,
              scores: {},
            },
          ],
        });
      if (path.endsWith("/reveal"))
        return Promise.reject(new ApiErrorCtor("Batch not fully submitted"));
      return Promise.resolve({ data: {} });
    });
    await loadBatch();
    fireEvent.click(screen.getByText("Reveal identities"));
    expect(await screen.findByText("Batch not fully submitted")).toBeDefined();
    expect(screen.queryByText(/Bradley-Terry/)).toBeNull();
  });
});
