import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-response-transformer-card";

describe("ResponseTransformerCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", rules: [{ rule_id: "r1", operation: "mask", source_field: "ssn" }], enabled: true }];
    const { container } = render(<Card configs={configs} totalTransformed={5000} appName="App" />);
    expect(container.textContent).toContain("Response Transformer");
    expect(container.textContent).toContain("5,000 transformed");
    expect(container.textContent).toContain("ssn");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} totalTransformed={0} appName="App" />);
    expect(container.textContent).toContain("No transform configs");
  });
});
