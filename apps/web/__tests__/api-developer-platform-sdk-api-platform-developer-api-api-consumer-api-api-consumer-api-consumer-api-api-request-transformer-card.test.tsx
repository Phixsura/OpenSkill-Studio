import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-request-transformer-card";

describe("ConsumerApiRequestTransformerCard", () => {
  it("shows rules", () => {
    const rules = [{ id: "r1", target: "header", action: "add", field: "X-Custom", value: "hello" }];
    const { container } = render(<Card rules={rules} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Request Transformer");
    expect(container.textContent).toContain("add");
    expect(container.textContent).toContain("X-Custom");
    expect(container.textContent).toContain("hello");
  });
  it("shows empty", () => {
    const { container } = render(<Card rules={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No transform rules");
  });
});
