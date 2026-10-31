import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRedisPanel } from "@/components/fleet-redis-panel";
describe("FleetRedisPanel", () => { it("renders", () => {
    const { container } = render(<FleetRedisPanel nodes={6} masters={3} replicas={3} totalKeys={5000000} memoryPct={60} healthy={true} />);
    expect(container.textContent).toContain("Redis");
    expect(container.textContent).toContain("5,000,000 keys");
}); });
