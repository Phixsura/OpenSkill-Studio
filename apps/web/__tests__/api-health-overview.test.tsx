import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiHealthOverview } from "@/components/api-health-overview";

describe("ApiHealthOverview", () => {
  it("renders health", () => {
    const { container } = render(
      <ApiHealthOverview totalEndpoints={10} healthy={8} healthPct={80}
        avgLatencyMs={120} avgErrorRate={1.5} overall="degraded"
        slowest={{ endpoint: "/billing", latencyMs: 2000 }}
        mostErrors={{ endpoint: "/billing", errorRate: 15 }} />
    );
    expect(container.textContent).toContain("API Health");
    expect(container.textContent).toContain("degraded");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("120ms");
    expect(container.textContent).toContain("/billing");
    expect(container.textContent).toContain("2000ms");
  });
});
