import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangeDiffPanel } from "@/components/change-diff-panel";
describe("ChangeDiffPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ChangeDiffPanel added={5} removed={2} changed={3} risk="high" totalDiffs={10} />
    );
    expect(container.textContent).toContain("Change Diff");
    expect(container.textContent).toContain("high risk");
    expect(container.textContent).toContain("+5");
    expect(container.textContent).toContain("-2");
    expect(container.textContent).toContain("~3");
  });
});
