import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-traffic-split-card";

describe("TrafficSplitCard", () => {
  it("shows splits", () => {
    const splits = [{ split_id: "s1", endpoint: "/api", targets: [{ version: "v1", weight: 80, upstream: "http://v1" }, { version: "v2", weight: 20, upstream: "http://v2" }], sticky: true }];
    const { container } = render(<Card splits={splits} appName="App" />);
    expect(container.textContent).toContain("Traffic Splits");
    expect(container.textContent).toContain("/api");
    expect(container.textContent).toContain("v1");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("sticky");
  });
  it("shows empty", () => {
    const { container } = render(<Card splits={[]} appName="App" />);
    expect(container.textContent).toContain("No traffic splits");
  });
});
