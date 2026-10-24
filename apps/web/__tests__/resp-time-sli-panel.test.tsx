import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RespTimeSliPanel } from "@/components/resp-time-sli-panel";
describe("RespTimeSliPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RespTimeSliPanel sliPct={99.5} samples={10000} thresholdMs={200}
        goodCount={9950} badCount={50} trend="improving" />
    );
    expect(container.textContent).toContain("Response Time SLI");
    expect(container.textContent).toContain("99.5% good");
    expect(container.textContent).toContain("200ms threshold");
    expect(container.textContent).toContain("9950");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("improving");
  });
});
