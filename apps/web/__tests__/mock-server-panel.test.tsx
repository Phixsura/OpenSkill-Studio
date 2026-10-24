import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MockServerPanel } from "@/components/mock-server-panel";
describe("MockServerPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MockServerPanel totalCalls={50}
        mocks={[
          { key: "GET /api/users", status: 200, calls: 30, delayMs: 0 },
          { key: "POST /api/orders", status: 201, calls: 20, delayMs: 100 },
        ]} />
    );
    expect(container.textContent).toContain("Mock Server");
    expect(container.textContent).toContain("2 mocks");
    expect(container.textContent).toContain("50 calls");
    expect(container.textContent).toContain("GET /api/users");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("100ms delay");
  });
});
