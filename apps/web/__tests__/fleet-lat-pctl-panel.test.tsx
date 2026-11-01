import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLatPctlPanel } from "@/components/fleet-lat-pctl-panel";
describe("FleetLatPctlPanel", () => { it("renders", () => {
    const { container } = render(<FleetLatPctlPanel p50={50} p95={200} p99={500} count={1000} />);
    expect(container.textContent).toContain("Latency Percentiles");
    expect(container.textContent).toContain("200ms");
}); });
