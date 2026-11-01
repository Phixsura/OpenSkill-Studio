import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMemoryPanel } from "@/components/fleet-memory-panel";
describe("FleetMemoryPanel", () => { it("renders", () => {
    const { container } = render(<FleetMemoryPanel usedMb={1700} allocMb={2048} pct={83} pressure={false} />);
    expect(container.textContent).toContain("Fleet Memory");
    expect(container.textContent).toContain("1,700");
}); });
