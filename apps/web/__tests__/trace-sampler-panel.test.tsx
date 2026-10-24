import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TraceSamplerPanel } from "@/components/trace-sampler-panel";
describe("TraceSamplerPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TraceSamplerPanel sampled={500} total={5000} actualRatePct={10} currentRate={0.1} />
    );
    expect(container.textContent).toContain("Adaptive Sampler");
    expect(container.textContent).toContain("10.0%");
    expect(container.textContent).toContain("10% actual");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("5,000");
  });
});
