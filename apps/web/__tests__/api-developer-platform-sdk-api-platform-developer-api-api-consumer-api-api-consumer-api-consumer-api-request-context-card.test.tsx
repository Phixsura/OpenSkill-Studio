import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-request-context-card";

describe("ConsumerApiRequestContextCard", () => {
  it("shows contexts", () => {
    const contexts = [{ id: "ctx1", traceId: "abcdef1234567890abcdef1234567890", spanId: "1234567890abcdef", parentSpanId: null, attributes: { method: "POST" }, baggageCount: 2 }];
    const { container } = render(<Card contexts={contexts} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Request Context");
    expect(container.textContent).toContain("abcdef1234567890");
    expect(container.textContent).toContain("method=POST");
    expect(container.textContent).toContain("2 baggage");
  });
  it("shows empty", () => {
    const { container } = render(<Card contexts={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No active contexts");
  });
});
