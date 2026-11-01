import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetStorageClassPanel } from "@/components/fleet-storage-class-panel";
describe("FleetStorageClassPanel", () => { it("renders", () => {
    const { container } = render(<FleetStorageClassPanel usedGb={700} allocGb={1000} pct={70} pressure={false} />);
    expect(container.textContent).toContain("Fleet Storage");
    expect(container.textContent).toContain("700 / 1000 GB");
}); });
