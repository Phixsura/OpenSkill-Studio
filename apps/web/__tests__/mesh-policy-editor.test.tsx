import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MeshPolicyEditor } from "@/components/mesh-policy-editor";

describe("MeshPolicyEditor", () => {
  it("renders", () => {
    const { container } = render(
      <MeshPolicyEditor cbCoveragePct={67} onAdd={vi.fn()} policies={[
        { name: "a", source: "api", destination: "db", timeoutMs: 5000, retries: 2, circuitBreaker: true },
        { name: "b", source: "web", destination: "api", timeoutMs: 30000, retries: 3, circuitBreaker: false },
      ]} />
    );
    expect(container.textContent).toContain("Mesh Policies");
    expect(container.textContent).toContain("2 policies");
    expect(container.textContent).toContain("67% CB");
    expect(container.textContent).toContain("api → db");
    expect(container.textContent).toContain("5000ms");
    expect(container.textContent).toContain("CB");
  });
});
