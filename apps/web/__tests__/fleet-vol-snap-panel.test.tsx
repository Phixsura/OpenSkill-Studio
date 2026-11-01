import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetVolSnapPanel } from "@/components/fleet-vol-snap-panel";
describe("FleetVolSnapPanel", () => { it("renders", () => {
    const { container } = render(<FleetVolSnapPanel total={10} withSnapshot={10} staleSnapshots={2} allFresh={false} />);
    expect(container.textContent).toContain("Volume Snapshots");
    expect(container.textContent).toContain("2 stale");
}); });
