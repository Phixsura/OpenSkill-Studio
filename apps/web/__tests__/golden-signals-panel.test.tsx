import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GoldenSignalsPanel } from "@/components/golden-signals-panel";
describe("GoldenSignalsPanel", () => {
  it("renders", () => {
    const { container } = render(
      <GoldenSignalsPanel status="healthy"
        signals={[
          { label: "Latency", value: "100ms", ok: true },
          { label: "Traffic", value: "500rps", ok: true },
          { label: "Errors", value: "0.1%", ok: true },
          { label: "Saturation", value: "50%", ok: true },
        ]} />
    );
    expect(container.textContent).toContain("Golden Signals: HEALTHY");
    expect(container.textContent).toContain("Latency");
    expect(container.textContent).toContain("100ms");
    expect(container.textContent).toContain("Traffic");
    expect(container.textContent).toContain("Saturation");
  });
});
