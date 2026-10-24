import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDepVulnPanel } from "@/components/fleet-dep-vuln-panel";
describe("FleetDepVulnPanel", () => { it("renders", () => {
    const { container } = render(<FleetDepVulnPanel totalDeps={200} critical={3} high={5} totalCves={15} clean={false} />);
    expect(container.textContent).toContain("Dep Vulnerabilities");
    expect(container.textContent).toContain("15 CVEs");
}); });
