import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageAnalyticsDash } from "@/components/usage-analytics-dash";

describe("UsageAnalyticsDash", () => {
  it("renders", () => {
    const { container } = render(
      <UsageAnalyticsDash totalRequests={1000} uniqueEndpoints={3}
        endpoints={[
          { endpoint: "/users", count: 500, avgMs: 55, errorRate: 0.5 },
          { endpoint: "/orders", count: 300, avgMs: 100, errorRate: 10 },
        ]} />
    );
    expect(container.textContent).toContain("API Usage");
    expect(container.textContent).toContain("1,000 reqs");
    expect(container.textContent).toContain("3 endpoints");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("500 calls");
    expect(container.textContent).toContain("10% err");
  });
});
