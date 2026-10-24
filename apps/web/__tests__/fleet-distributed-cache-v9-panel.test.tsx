import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDistributedCacheV9Panel } from "@/components/fleet-distributed-cache-v9-panel";
describe("FleetDistributedCacheV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDistributedCacheV9Panel nodes={12} hitRate={95} />);
    expect(container.textContent).toContain("Distributed Cache v9");
}); });
