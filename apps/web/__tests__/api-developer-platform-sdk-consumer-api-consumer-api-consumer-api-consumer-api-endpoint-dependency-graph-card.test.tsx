import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-api-consumer-api-consumer-api-endpoint-dependency-graph-card";

describe("EndpointDependencyGraphCard", () => {
  it("shows graph", () => {
    const nodes = [{ path: "/gateway", incoming: 0, outgoing: 2, isRoot: true, isLeaf: false }, { path: "/users", incoming: 1, outgoing: 0, isRoot: false, isLeaf: true }];
    const edges = [{ from: "/gateway", to: "/users", callCount: 100, avgMs: 50 }];
    const { container } = render(<Card nodes={nodes} edges={edges} maxDepth={1} appName="App" />);
    expect(container.textContent).toContain("Dependency Graph");
    expect(container.textContent).toContain("/gateway");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("root:");
    expect(container.textContent).toContain("leaf:");
  });
  it("shows empty", () => {
    const { container } = render(<Card nodes={[]} edges={[]} maxDepth={0} appName="App" />);
    expect(container.textContent).toContain("No dependencies");
  });
});
