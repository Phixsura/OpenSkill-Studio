import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-request-tracing-config-card";

describe("RequestTracingConfigCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", enabled: true, sample_rate: 0.5, propagation: "w3c", export_format: "otlp" }];
    const { container } = render(<Card configs={configs} appName="App" />);
    expect(container.textContent).toContain("Tracing Config");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("w3c");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} appName="App" />);
    expect(container.textContent).toContain("No tracing configs");
  });
});
