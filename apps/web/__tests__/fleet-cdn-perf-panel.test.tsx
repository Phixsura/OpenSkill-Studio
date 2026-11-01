import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCdnPerfPanel } from "@/components/fleet-cdn-perf-panel";
describe("FleetCdnPerfPanel", () => { it("renders", () => {
    const { container } = render(<FleetCdnPerfPanel hitRate={92.5} avgLatency={25} pops={10} effective={true} />);
    expect(container.textContent).toContain("CDN Performance");
    expect(container.textContent).toContain("Effective");
}); });
