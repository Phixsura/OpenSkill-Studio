import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LatencyTrackPanel } from "@/components/latency-track-panel";
describe("LatencyTrackPanel", () => {
  it("renders", () => {
    const { container } = render(
      <LatencyTrackPanel total={100}
        buckets={{ "<10ms": 50, "10-50ms": 30, "50-100ms": 10, "100-500ms": 8, ">500ms": 2 }} />
    );
    expect(container.textContent).toContain("Latency Distribution");
    expect(container.textContent).toContain("100 samples");
    expect(container.textContent).toContain("<10ms");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain(">500ms");
  });
});
