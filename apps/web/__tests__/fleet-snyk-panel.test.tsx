import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSnykPanel } from "@/components/fleet-snyk-panel";
describe("FleetSnykPanel", () => { it("renders", () => {
    const { container } = render(<FleetSnykPanel total={50} clean={45} totalIssues={20} critical={2} />);
    expect(container.textContent).toContain("Snyk");
    expect(container.textContent).toContain("2 critical");
}); });
