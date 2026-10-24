import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrafficMirrorPanel } from "@/components/traffic-mirror-panel";

describe("TrafficMirrorPanel", () => {
  it("renders mirrors", () => {
    const { container } = render(
      <TrafficMirrorPanel totalMirrored={1100} active={2} mirrors={[
        { source: "prod-api", target: "shadow-api", sampleRate: 0.5, mirrored: 1000, errors: 5, status: "active" },
        { source: "web", target: "shadow-web", sampleRate: 0.1, mirrored: 100, errors: 0, status: "active" },
      ]} />
    );
    expect(container.textContent).toContain("Traffic Mirroring");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("1100 mirrored");
    expect(container.textContent).toContain("prod-api → shadow-api");
    expect(container.textContent).toContain("50% sampled");
  });
});
