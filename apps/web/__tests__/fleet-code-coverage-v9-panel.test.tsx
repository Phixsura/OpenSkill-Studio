import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCodeCoverageV9Panel } from "@/components/fleet-code-coverage-v9-panel";
describe("FleetCodeCoverageV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCodeCoverageV9Panel repos={20} coverage={92} />);
    expect(container.textContent).toContain("Code Coverage v9");
}); });
