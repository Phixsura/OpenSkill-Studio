import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshShapePanel } from "@/components/mesh-shape-panel";
describe("MeshShapePanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshShapePanel activeCount={2}
        rules={[
          { source: "api", destination: "db", type: "delay", active: true },
          { source: "api", destination: "db", type: "rate_limit", active: true },
        ]} />
    );
    expect(container.textContent).toContain("Traffic Shaping");
    expect(container.textContent).toContain("2 active rules");
    expect(container.textContent).toContain("api → db");
    expect(container.textContent).toContain("delay");
    expect(container.textContent).toContain("rate_limit");
  });
});
