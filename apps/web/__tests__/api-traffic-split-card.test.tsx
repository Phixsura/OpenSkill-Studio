import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APITrafficSplitCard from "../src/components/api-traffic-split-card";

const targets = [
  { version: "v1", weight: 90, request_count: 9000 },
  { version: "v2", weight: 10, request_count: 1000 },
];

describe("APITrafficSplitCard", () => {
  it("renders header and total", () => {
    const { container } = render(<APITrafficSplitCard targets={targets} splitId="s1" appName="App" />);
    expect(container.textContent).toContain("Traffic Split");
    expect(container.textContent).toContain("10,000 routed");
  });

  it("shows versions with weights", () => {
    const { container } = render(<APITrafficSplitCard targets={targets} splitId="s1" appName="App" />);
    expect(container.textContent).toContain("v1");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("v2");
    expect(container.textContent).toContain("10%");
  });

  it("shows empty state", () => {
    const { container } = render(<APITrafficSplitCard targets={[]} splitId="s1" appName="App" />);
    expect(container.textContent).toContain("No traffic split");
  });
});
