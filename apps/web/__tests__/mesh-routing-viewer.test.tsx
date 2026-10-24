import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshRoutingViewer } from "@/components/mesh-routing-viewer";

describe("MeshRoutingViewer", () => {
  it("renders", () => {
    const { container } = render(
      <MeshRoutingViewer
        rules={[
          { name: "v2-route", destination: "api-v2",
            conditions: [{ field: "path", op: "prefix", value: "/api/v2" }] },
        ]}
        splits={[
          { destination: "canary", pct: 10 },
          { destination: "stable", pct: 90 },
        ]} />
    );
    expect(container.textContent).toContain("Mesh Routing");
    expect(container.textContent).toContain("1 rules");
    expect(container.textContent).toContain("v2-route");
    expect(container.textContent).toContain("api-v2");
    expect(container.textContent).toContain("Traffic Split");
  });
});
