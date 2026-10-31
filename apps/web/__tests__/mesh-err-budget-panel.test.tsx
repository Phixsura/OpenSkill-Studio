import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshErrBudgetPanel } from "@/components/mesh-err-budget-panel";
describe("MeshErrBudgetPanel", () => { it("renders", () => {
    const { container } = render(<MeshErrBudgetPanel exhausted={1} total={5} allWithin={false} />);
    expect(container.textContent).toContain("Mesh Error Budget");
    expect(container.textContent).toContain("1 exhausted");
}); });
