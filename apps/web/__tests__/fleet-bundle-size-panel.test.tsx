import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBundleSizePanel } from "@/components/fleet-bundle-size-panel";
describe("FleetBundleSizePanel", () => { it("renders", () => {
    const { container } = render(<FleetBundleSizePanel totalKb={550} bundles={10} large={2} optimized={false} />);
    expect(container.textContent).toContain("Bundle Size");
    expect(container.textContent).toContain("2 oversized");
}); });
