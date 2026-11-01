import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqSamplingPanel } from "@/components/req-sampling-panel";
describe("ReqSamplingPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReqSamplingPanel totalSeen={10000} captured={100} sampleRate={0.01} />
    );
    expect(container.textContent).toContain("Request Sampling");
    expect(container.textContent).toContain("1.0% rate");
    expect(container.textContent).toContain("100 captured");
    expect(container.textContent).toContain("10,000");
  });
});
