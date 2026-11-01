import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiMockManager } from "@/components/api-mock-manager";

describe("ApiMockManager", () => {
  it("renders mocks", () => {
    const { container } = render(
      <ApiMockManager totalHits={15} onAdd={vi.fn()} onClear={vi.fn()} mocks={[
        { method: "GET", path: "/api/users", status: 200, hitCount: 10, delayMs: 0 },
        { method: "POST", path: "/api/orders", status: 201, hitCount: 5, delayMs: 100 },
      ]} />
    );
    expect(container.textContent).toContain("API Mocks");
    expect(container.textContent).toContain("2 mocks");
    expect(container.textContent).toContain("15 hits");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("100ms delay");
  });
});
