import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDistributedLockV9Panel } from "@/components/fleet-distributed-lock-v9-panel";
describe("FleetDistributedLockV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDistributedLockV9Panel locks={100} contended={2} />);
    expect(container.textContent).toContain("Distributed Lock v9");
}); });
