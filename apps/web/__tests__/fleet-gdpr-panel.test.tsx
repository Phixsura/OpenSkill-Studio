import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGdprPanel } from "@/components/fleet-gdpr-panel";
describe("FleetGdprPanel", () => { it("renders", () => {
    const { container } = render(<FleetGdprPanel total={20} met={18} unmet={2} score={90} compliant={false} />);
    expect(container.textContent).toContain("GDPR");
    expect(container.textContent).toContain("90%");
}); });
