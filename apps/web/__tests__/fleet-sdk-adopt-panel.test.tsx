import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSdkAdoptPanel } from "@/components/fleet-sdk-adopt-panel";
describe("FleetSdkAdoptPanel", () => { it("renders", () => {
    const { container } = render(<FleetSdkAdoptPanel total={100} outdated={20} upToDate={80} />);
    expect(container.textContent).toContain("SDK Adoption");
    expect(container.textContent).toContain("20 need upgrade");
}); });
