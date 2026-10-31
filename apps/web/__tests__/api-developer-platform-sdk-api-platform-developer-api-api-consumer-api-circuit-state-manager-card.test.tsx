import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-circuit-state-manager-card";

describe("CircuitStateManagerCard", () => {
  it("shows circuits", () => {
    const circuits = [{ consumer_id: "c1", endpoint: "/api", state: "open", failure_count: 5, total_transitions: 3 }];
    const { container } = render(<Card circuits={circuits} openCount={1} appName="App" />);
    expect(container.textContent).toContain("Circuit States");
    expect(container.textContent).toContain("1 open");
    expect(container.textContent).toContain("c1 → /api");
  });
  it("shows empty", () => {
    const { container } = render(<Card circuits={[]} openCount={0} appName="App" />);
    expect(container.textContent).toContain("No circuits");
  });
});
