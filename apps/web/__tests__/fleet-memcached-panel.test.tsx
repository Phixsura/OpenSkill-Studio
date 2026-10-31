import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMemcachedPanel } from "@/components/fleet-memcached-panel";
describe("FleetMemcachedPanel", () => { it("renders", () => {
    const { container } = render(<FleetMemcachedPanel nodes={10} alive={10} items={50000000} hitRate={95} />);
    expect(container.textContent).toContain("Memcached");
    expect(container.textContent).toContain("95% hit");
}); });
