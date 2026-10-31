import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EpHealthPanel } from "@/components/ep-health-panel";
describe("EpHealthPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EpHealthPanel endpoints={[
        { endpoint: "/api/users", status: "healthy", errorRate: 0, avgMs: 50, totalRequests: 1000 },
        { endpoint: "/api/orders", status: "unhealthy", errorRate: 10, avgMs: 200, totalRequests: 500 },
      ]} />
    );
    expect(container.textContent).toContain("Endpoint Health");
    expect(container.textContent).toContain("2 endpoints");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("0% err");
    expect(container.textContent).toContain("/api/orders");
    expect(container.textContent).toContain("10% err");
  });
});
