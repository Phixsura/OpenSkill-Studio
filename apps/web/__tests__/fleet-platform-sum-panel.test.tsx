import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPlatformSumPanel } from "@/components/fleet-platform-sum-panel";
describe("FleetPlatformSumPanel", () => { it("renders", () => {
    const { container } = render(<FleetPlatformSumPanel score={100} grade="A" />);
    expect(container.textContent).toContain("Platform Health");
    expect(container.textContent).toContain("100 — A");
}); });
