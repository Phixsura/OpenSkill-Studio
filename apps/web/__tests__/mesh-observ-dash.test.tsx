import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshObservDash } from "@/components/mesh-observ-dash";

describe("MeshObservDash", () => {
  it("renders", () => {
    const { container } = render(
      <MeshObservDash totalFlows={1000} totalErrors={10}
        pairs={[
          { source: "web", destination: "api", count: 600, avgMs: 12, errorRate: 0.5 },
          { source: "api", destination: "db", count: 400, avgMs: 8, errorRate: 2.5 },
        ]} />
    );
    expect(container.textContent).toContain("Mesh Traffic");
    expect(container.textContent).toContain("1,000 flows");
    expect(container.textContent).toContain("10 errors");
    expect(container.textContent).toContain("web → api");
    expect(container.textContent).toContain("600");
    expect(container.textContent).toContain("12ms");
  });
});
