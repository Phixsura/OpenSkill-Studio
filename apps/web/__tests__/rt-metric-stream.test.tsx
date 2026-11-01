import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RtMetricStream } from "@/components/rt-metric-stream";

describe("RtMetricStream", () => {
  it("renders stream", () => {
    const { container } = render(
      <RtMetricStream stream="cpu_pct" latest={48} avg={48.33} min={45} max={52} count={100} />
    );
    expect(container.textContent).toContain("cpu_pct");
    expect(container.textContent).toContain("100 points");
    expect(container.textContent).toContain("48");
    expect(container.textContent).toContain("48.33");
    expect(container.textContent).toContain("45");
    expect(container.textContent).toContain("52");
  });
});
