import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTrivyPanel } from "@/components/fleet-trivy-panel";
describe("FleetTrivyPanel", () => { it("renders", () => {
    const { container } = render(<FleetTrivyPanel totalScans={50} clean={45} critical={3} high={8} allClean={false} />);
    expect(container.textContent).toContain("Trivy");
    expect(container.textContent).toContain("3 critical");
}); });
