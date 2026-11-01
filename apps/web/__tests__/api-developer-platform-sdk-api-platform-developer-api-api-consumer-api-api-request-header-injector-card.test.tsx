import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-header-injector-card";

describe("RequestHeaderInjectorCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", rules: [{ rule_id: "r1", header_name: "X-Source", override: false }] }];
    const { container } = render(<Card configs={configs} appName="App" />);
    expect(container.textContent).toContain("Header Injector");
    expect(container.textContent).toContain("X-Source");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} appName="App" />);
    expect(container.textContent).toContain("No injection configs");
  });
});
