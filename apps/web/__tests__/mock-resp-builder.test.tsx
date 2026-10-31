import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MockRespBuilder } from "@/components/mock-resp-builder";

describe("MockRespBuilder", () => {
  it("renders", () => {
    const { container } = render(
      <MockRespBuilder total={3} byMethod={{ GET: 2, POST: 1 }} onAdd={vi.fn()}
        mocks={[
          { path: "/api/users", method: "GET", status: 200, delayMs: 0 },
          { path: "/api/orders", method: "POST", status: 201, delayMs: 100 },
        ]} />
    );
    expect(container.textContent).toContain("Mock Responses");
    expect(container.textContent).toContain("3 mocks");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("201");
    expect(container.textContent).toContain("100ms");
  });
});
