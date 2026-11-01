import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ThrottleStatusIndicator } from "@/components/throttle-status-indicator";

describe("ThrottleStatusIndicator", () => {
  it("normal", () => {
    const { container } = render(
      <ThrottleStatusIndicator currentRps={50} effectiveMaxRps={100} throttled={false}
        delayMs={0} recommendation="normal" loadFactor={0.4} />
    );
    expect(container.textContent).toContain("Throttle Status");
    expect(container.textContent).toContain("normal");
    expect(container.textContent).toContain("50 RPS");
  });
  it("throttled", () => {
    const { container } = render(
      <ThrottleStatusIndicator currentRps={150} effectiveMaxRps={80} throttled={true}
        delayMs={500} recommendation="throttle" loadFactor={0.85} />
    );
    expect(container.textContent).toContain("throttle");
    expect(container.textContent).toContain("+500ms delay");
  });
});
