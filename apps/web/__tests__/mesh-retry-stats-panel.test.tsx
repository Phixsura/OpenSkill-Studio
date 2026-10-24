import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshRetryStatsPanel } from "@/components/mesh-retry-stats-panel";
describe("MeshRetryStatsPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshRetryStatsPanel totalRetries={200} totalRequests={10000}
        pairs={[{ pair: "api→db", total: 5000, retries: 200, retryRate: 4, retrySuccessRate: 80 }]} />
    );
    expect(container.textContent).toContain("Mesh Retry Analytics");
    expect(container.textContent).toContain("200 retries / 10,000 total");
    expect(container.textContent).toContain("api→db");
    expect(container.textContent).toContain("200 retries (4%)");
    expect(container.textContent).toContain("80% recovered");
  });
});
