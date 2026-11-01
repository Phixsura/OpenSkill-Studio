import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiUsageInsights } from "@/components/api-usage-insights";

describe("ApiUsageInsights", () => {
  it("renders insights", () => {
    const { container } = render(
      <ApiUsageInsights totalRequests={10000} avgLatencyMs={85} errorRatePct={2.5}
        topEndpoint="GET /users" byMethod={{ GET: 7000, POST: 3000 }}
        byStatus={{ "200": 9500, "500": 250, "404": 250 }} />
    );
    expect(container.textContent).toContain("API Usage");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("85ms");
    expect(container.textContent).toContain("2.5%");
    expect(container.textContent).toContain("GET /users");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("7000");
  });
});
