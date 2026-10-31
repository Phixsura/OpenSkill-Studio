import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshLatBudgetPanel } from "@/components/mesh-lat-budget-panel";
describe("MeshLatBudgetPanel", () => { it("renders", () => {
    const { container } = render(<MeshLatBudgetPanel overBudget={1} total={5} allWithin={false} />);
    expect(container.textContent).toContain("Mesh Latency Budget");
    expect(container.textContent).toContain("1/5 over budget");
}); });
