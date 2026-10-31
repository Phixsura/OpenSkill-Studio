import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCacheRatioPanel } from "@/components/fleet-cache-ratio-panel";
describe("FleetCacheRatioPanel", () => { it("renders", () => {
    const { container } = render(<FleetCacheRatioPanel ratioPct={85} hits={1700} misses={300} effective={true} />);
    expect(container.textContent).toContain("Fleet Cache Hit Ratio");
    expect(container.textContent).toContain("85%");
}); });
