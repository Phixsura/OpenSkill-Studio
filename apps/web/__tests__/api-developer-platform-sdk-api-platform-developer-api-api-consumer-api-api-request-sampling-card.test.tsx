import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-sampling-card";

describe("RequestSamplingCard", () => {
  it("shows sampling info", () => {
    const { container } = render(<Card sampleCount={2500} sampleRate={0.01} avgDuration={45} maxSamples={5000} appName="App" />);
    expect(container.textContent).toContain("Request Sampling");
    expect(container.textContent).toContain("1.0% rate");
    expect(container.textContent).toContain("2,500");
    expect(container.textContent).toContain("45ms");
  });
  it("shows zero", () => {
    const { container } = render(<Card sampleCount={0} sampleRate={0.05} avgDuration={0} maxSamples={1000} appName="App" />);
    expect(container.textContent).toContain("5.0% rate");
  });
});
