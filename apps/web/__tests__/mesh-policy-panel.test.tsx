import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshPolicyPanel } from "@/components/mesh-policy-panel";
describe("MeshPolicyPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshPolicyPanel avgTimeoutMs={2000}
        policies={[
          { source: "api", destination: "db", timeoutMs: 3000, retries: 5, circuitBreakThreshold: 5 },
          { source: "api", destination: "cache", timeoutMs: 1000, retries: 1, circuitBreakThreshold: 3 },
        ]} />
    );
    expect(container.textContent).toContain("Mesh Policies");
    expect(container.textContent).toContain("2 policies");
    expect(container.textContent).toContain("avg 2000ms");
    expect(container.textContent).toContain("api → db");
    expect(container.textContent).toContain("3000ms");
    expect(container.textContent).toContain("5 retries");
  });
});
