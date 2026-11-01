import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DocCoveragePanel } from "@/components/doc-coverage-panel";
describe("DocCoveragePanel", () => {
  it("renders", () => {
    const { container } = render(
      <DocCoveragePanel overallPct={75} grade="B" totalEndpoints={20}
        scores={{ description: 90, examples: 60, parameters: 80, error_codes: 70 }} />
    );
    expect(container.textContent).toContain("Doc Coverage");
    expect(container.textContent).toContain("75%");
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("20 endpoints");
    expect(container.textContent).toContain("description");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("examples");
  });
});
