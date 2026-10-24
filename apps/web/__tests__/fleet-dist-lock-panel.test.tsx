import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDistLockPanel } from "@/components/fleet-dist-lock-panel";
describe("FleetDistLockPanel", () => { it("renders", () => {
    const { container } = render(<FleetDistLockPanel activeLocks={5} contention={50} deadlocks={0} healthy={true} />);
    expect(container.textContent).toContain("Dist Locks");
    expect(container.textContent).toContain("0 deadlocks");
}); });
