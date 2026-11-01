import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SpanSamplerPanel } from "@/components/span-sampler-panel";

describe("SpanSamplerPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SpanSamplerPanel sampled={500} dropped={500} actualRatePct={50}
        configuredRate={0.5} strategy="probabilistic" />
    );
    expect(container.textContent).toContain("Span Sampler");
    expect(container.textContent).toContain("probabilistic");
    expect(container.textContent).toContain("50% configured");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("50%");
  });
});
