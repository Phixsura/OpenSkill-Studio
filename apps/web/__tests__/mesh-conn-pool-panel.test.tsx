import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshConnPoolPanel } from "@/components/mesh-conn-pool-panel";
describe("MeshConnPoolPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshConnPoolPanel saturated={1} healthy={1}
        pools={[
          { service: "api", destination: "db", active: 18, maxSize: 20, utilPct: 90, saturated: true },
          { service: "api", destination: "cache", active: 5, maxSize: 20, utilPct: 25, saturated: false },
        ]} />
    );
    expect(container.textContent).toContain("Mesh Conn Pools");
    expect(container.textContent).toContain("1 healthy");
    expect(container.textContent).toContain("1 saturated");
    expect(container.textContent).toContain("api→db");
    expect(container.textContent).toContain("18/20");
  });
});
