import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqSamplingPanel } from "@/components/req-sampling-panel";

describe("ReqSamplingPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReqSamplingPanel total={10000} sampled={1050} dropped={8950}
        targetRate={0.1} actualRate={0.105} deviationPct={5} accurate={false} />
    );
    expect(container.textContent).toContain("Request Sampling");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("1,050");
    expect(container.textContent).toContain("10.0%");
    expect(container.textContent).toContain("10.5%");
    expect(container.textContent).toContain("5% deviation");
  });
});
