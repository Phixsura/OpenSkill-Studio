import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSevDistPanel } from "@/components/fleet-sev-dist-panel";
describe("FleetSevDistPanel", () => { it("renders", () => {
    const { container } = render(<FleetSevDistPanel total={20} sev1Count={2} critical={true} />);
    expect(container.textContent).toContain("Severity Distribution");
    expect(container.textContent).toContain("Critical incidents");
}); });
