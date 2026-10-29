import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-endpoint-dependency-graph-card";

const nodes = [{ endpoint_id: "e1", method: "GET", path: "/users", dep_count: 2, dependent_count: 1 }];

describe("DependencyGraphCard", () => {
  it("shows graph info", () => {
    const { container } = render(<Card nodes={nodes} cycleCount={1} appName="App" />);
    expect(container.textContent).toContain("Endpoint Dependencies");
    expect(container.textContent).toContain("1 cycle");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/users");
  });
  it("shows empty", () => {
    const { container } = render(<Card nodes={[]} cycleCount={0} appName="App" />);
    expect(container.textContent).toContain("No endpoints mapped");
  });
});
