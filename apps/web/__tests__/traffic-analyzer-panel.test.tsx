import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrafficAnalyzerPanel } from "@/components/traffic-analyzer-panel";

describe("TrafficAnalyzerPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TrafficAnalyzerPanel totalRequests={10000} avgLatencyMs={85} errorPct={1.5}
        topPath="/api/users" topPathCount={5000}
        byMethod={{ GET: 7000, POST: 3000 }}
        byStatus={{ "200": 9500, "500": 150, "404": 350 }} />
    );
    expect(container.textContent).toContain("Traffic Analysis");
    expect(container.textContent).toContain("10,000 requests");
    expect(container.textContent).toContain("85ms");
    expect(container.textContent).toContain("1.5% errors");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("7000");
  });
});
