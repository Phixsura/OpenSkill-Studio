import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSnapshotMgrV9Panel } from "@/components/fleet-snapshot-mgr-v9-panel";
describe("FleetSnapshotMgrV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSnapshotMgrV9Panel total={50} sizeGb={500} />);
    expect(container.textContent).toContain("Snapshot Manager v9");
}); });
