import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiTrafficSplitterCard from "../src/components/api-developer-api-api-traffic-splitter-card";

const rules = [
  { rule_id: "r1", endpoint: "/api/users", splits: { v1: 90, v2: 10 }, total_routed: 5000, per_version_count: { v1: 4500, v2: 500 } },
];

describe("APIDeveloperAPIApiTrafficSplitterCard", () => {
  it("shows split rules", () => {
    const { container } = render(<APIDeveloperAPIApiTrafficSplitterCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Traffic Splitter");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("5,000 routed");
    expect(container.textContent).toContain("v1: 90%");
    expect(container.textContent).toContain("v2: 10%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiTrafficSplitterCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No split rules");
  });
});
