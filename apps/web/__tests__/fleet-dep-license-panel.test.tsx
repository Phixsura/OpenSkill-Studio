import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDepLicensePanel } from "@/components/fleet-dep-license-panel";
describe("FleetDepLicensePanel", () => { it("renders", () => {
    const { container } = render(<FleetDepLicensePanel total={200} approved={195} copyleft={3} unknown={2} compliant={false} />);
    expect(container.textContent).toContain("Dep Licenses");
    expect(container.textContent).toContain("3 copyleft");
}); });
