import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPlatformSummaryV93 } from "@/components/fleet-platform-summary-v93";
describe("FleetPlatformSummaryV93", () => { it("renders", () => {
    const { container } = render(<FleetPlatformSummaryV93 />);
    expect(container.textContent).toContain("v93+");
    expect(container.textContent).toContain("332K+");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
