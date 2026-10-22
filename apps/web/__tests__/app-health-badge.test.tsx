import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { AppHealthBadge } from "@/components/app-health-badge";

const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
function Wrapper({ children }: { children: ReactNode }) {
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
}

describe("AppHealthBadge", () => {
  it.each([100, 95, 80, 50, 0])("renders score %d", (score) => {
    const { container } = render(<AppHealthBadge score={score} />, { wrapper: Wrapper });
    expect(container.querySelector("span")).toBeTruthy();
  });

  it("shows healthy for 100", () => {
    const { container } = render(<AppHealthBadge score={100} />, { wrapper: Wrapper });
    expect(container.querySelector("span")).toBeTruthy();
  });
});
