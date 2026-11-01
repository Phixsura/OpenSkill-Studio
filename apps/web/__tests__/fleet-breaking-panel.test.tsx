import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBreakingPanel } from "@/components/fleet-breaking-panel";
describe("FleetBreakingPanel", () => { it("renders", () => {
    const { container } = render(<FleetBreakingPanel totalChanges={10} breaking={2} withGuide={1} safe={false} />);
    expect(container.textContent).toContain("Breaking Changes");
    expect(container.textContent).toContain("2 breaking");
}); });
