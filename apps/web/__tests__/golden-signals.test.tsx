import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GoldenSignals } from "@/components/golden-signals";

describe("GoldenSignals", () => {
  it("renders", () => {
    const { container } = render(
      <GoldenSignals status="healthy" score={4}
        latency={{ value: 50, unit: "ms", ok: true }}
        traffic={{ value: 1000, unit: "rps", ok: true }}
        errors={{ value: 0.1, unit: "%", ok: true }}
        saturation={{ value: 45, unit: "%", ok: true }} />
    );
    expect(container.textContent).toContain("Golden Signals");
    expect(container.textContent).toContain("4/4");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("50ms");
    expect(container.textContent).toContain("1000rps");
    expect(container.textContent).toContain("0.1%");
    expect(container.textContent).toContain("45%");
  });
});
