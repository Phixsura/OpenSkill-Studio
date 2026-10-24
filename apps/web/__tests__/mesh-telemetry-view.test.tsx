import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshTelemetryView } from "@/components/mesh-telemetry-view";

describe("MeshTelemetryView", () => {
  it("renders telemetry", () => {
    const { container } = render(
      <MeshTelemetryView totalRequests={450} meshErrorRate={1.56} uniquePairs={3}
        connections={[
          { source: "api", destination: "cache", requests: 200, errors: 0, avgLatencyMs: 0.5, errorRatePct: 0 },
          { source: "web", destination: "api", requests: 150, errors: 5, avgLatencyMs: 5, errorRatePct: 3.3 },
        ]} />
    );
    expect(container.textContent).toContain("Mesh Telemetry");
    expect(container.textContent).toContain("3 pairs");
    expect(container.textContent).toContain("450 req");
    expect(container.textContent).toContain("api → cache");
    expect(container.textContent).toContain("web → api");
    expect(container.textContent).toContain("3.3% err");
  });
});
