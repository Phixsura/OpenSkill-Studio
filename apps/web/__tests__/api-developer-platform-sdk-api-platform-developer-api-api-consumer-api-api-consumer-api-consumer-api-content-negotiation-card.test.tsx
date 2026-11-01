import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-content-negotiation-card";

describe("ConsumerApiContentNegotiationCard", () => {
  it("shows config", () => {
    const { container } = render(<Card consumerId="c1" supportedFormats={["application/json", "text/csv"]} defaultFormat="application/json" strict={false} appName="App" />);
    expect(container.textContent).toContain("Content Negotiation");
    expect(container.textContent).toContain("json");
    expect(container.textContent).toContain("csv");
    expect(container.textContent).toContain("Flexible");
  });
  it("shows strict", () => {
    const { container } = render(<Card consumerId="c1" supportedFormats={["application/json"]} defaultFormat="application/json" strict={true} appName="App" />);
    expect(container.textContent).toContain("Strict");
  });
});
