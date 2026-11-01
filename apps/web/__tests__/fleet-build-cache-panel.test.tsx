import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBuildCachePanel } from "@/components/fleet-build-cache-panel";
describe("FleetBuildCachePanel", () => { it("renders", () => {
    const { container } = render(<FleetBuildCachePanel hitRate={80} timeSaved={600} builds={50} effective={true} />);
    expect(container.textContent).toContain("Build Cache");
    expect(container.textContent).toContain("80% hit rate");
}); });
