import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepWeightPanel } from "@/components/dep-weight-panel";
describe("DepWeightPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DepWeightPanel mostCritical="api" weights={{ api: 70, worker: 15 }} />
    );
    expect(container.textContent).toContain("Dependency Weights");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("70");
  });
});
