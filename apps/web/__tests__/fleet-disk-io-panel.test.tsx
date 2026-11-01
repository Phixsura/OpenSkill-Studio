import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDiskIoPanel } from "@/components/fleet-disk-io-panel";
describe("FleetDiskIoPanel", () => { it("renders", () => {
    const { container } = render(<FleetDiskIoPanel readMbps={700} writeMbps={400} totalIops={1100} saturated={true} />);
    expect(container.textContent).toContain("Fleet Disk I/O");
    expect(container.textContent).toContain("Disk saturated");
}); });
