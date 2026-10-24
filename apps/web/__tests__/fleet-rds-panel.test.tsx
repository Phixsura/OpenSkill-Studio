import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRdsPanel } from "@/components/fleet-rds-panel";
describe("FleetRdsPanel", () => { it("renders", () => {
    const { container } = render(<FleetRdsPanel instances={10} available={10} multiAz={8} storageGb={5000} />);
    expect(container.textContent).toContain("RDS");
    expect(container.textContent).toContain("8 multi-AZ");
}); });
