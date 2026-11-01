import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshLbPanel } from "@/components/mesh-lb-panel";
describe("MeshLbPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshLbPanel service="api" strategy="round_robin"
        backends={[
          { address: "10.0.0.1:8080", healthy: true, connections: 5 },
          { address: "10.0.0.2:8080", healthy: false, connections: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Mesh LB: api");
    expect(container.textContent).toContain("round_robin");
    expect(container.textContent).toContain("1/2 healthy");
    expect(container.textContent).toContain("10.0.0.1:8080");
    expect(container.textContent).toContain("5 conn");
  });
});
