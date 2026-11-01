import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLintScorePanel } from "@/components/fleet-lint-score-panel";
describe("FleetLintScorePanel", () => { it("renders", () => {
    const { container } = render(<FleetLintScorePanel totalRepos={20} clean={18} totalErrors={10} cleanPct={90} />);
    expect(container.textContent).toContain("Lint Score");
    expect(container.textContent).toContain("90%");
}); });
