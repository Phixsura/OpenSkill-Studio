import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshFaultPanel } from "@/components/mesh-fault-panel";
describe("MeshFaultPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshFaultPanel activeCount={1}
        rules={[
          { source: "api", destination: "db", faultType: "latency", percentage: 50, active: true },
          { source: "web", destination: "api", faultType: "error", percentage: 10, active: false },
        ]} />
    );
    expect(container.textContent).toContain("Mesh Fault Injection");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("api → db");
    expect(container.textContent).toContain("latency 50%");
    expect(container.textContent).toContain("ACTIVE");
  });
});
