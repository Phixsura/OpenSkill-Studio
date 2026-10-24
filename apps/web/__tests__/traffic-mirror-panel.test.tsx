import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrafficMirrorPanel } from "@/components/traffic-mirror-panel";
describe("TrafficMirrorPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TrafficMirrorPanel totalMirrored={5000}
        mirrors={[
          { source: "prod", target: "shadow", active: true, mirrored: 3000, samplePct: 100 },
          { source: "prod", target: "canary", active: false, mirrored: 2000, samplePct: 10 },
        ]} />
    );
    expect(container.textContent).toContain("Traffic Mirror");
    expect(container.textContent).toContain("5,000 mirrored");
    expect(container.textContent).toContain("prod → shadow");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("3,000");
  });
});
