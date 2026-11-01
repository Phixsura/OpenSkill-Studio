import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-endpoint-request-optimizer-card";

describe("EndpointRequestOptimizerCard", () => {
  it("shows suggestions", () => {
    const suggestions = [{ id: "s1", category: "caching", title: "Enable Caching", description: "Cache hit rate low", improvement: 30 }];
    const { container } = render(<Card suggestions={suggestions} totalSavings={30} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Request Optimizer");
    expect(container.textContent).toContain("Enable Caching");
    expect(container.textContent).toContain("~30%");
  });
  it("shows no suggestions", () => {
    const { container } = render(<Card suggestions={[]} totalSavings={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No optimizations needed");
  });
});
