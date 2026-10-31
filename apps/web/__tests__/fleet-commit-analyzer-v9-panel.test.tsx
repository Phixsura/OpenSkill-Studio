import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCommitAnalyzerV9Panel } from "@/components/fleet-commit-analyzer-v9-panel";
describe("FleetCommitAnalyzerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCommitAnalyzerV9Panel total={1000} conventional={950} />);
    expect(container.textContent).toContain("Commit Analyzer v9");
}); });
