import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSonarqubePanel } from "@/components/fleet-sonarqube-panel";
describe("FleetSonarqubePanel", () => { it("renders", () => {
    const { container } = render(<FleetSonarqubePanel total={30} passing={28} failing={2} avgCoverage={75} />);
    expect(container.textContent).toContain("SonarQube");
    expect(container.textContent).toContain("2 failing");
}); });
