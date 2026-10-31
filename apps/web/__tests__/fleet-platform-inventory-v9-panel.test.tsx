import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPlatformInventoryV9Panel } from "@/components/fleet-platform-inventory-v9-panel";
describe("FleetPlatformInventoryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPlatformInventoryV9Panel />);
    expect(container.textContent).toContain("Platform Inventory v9");
    expect(container.textContent).toContain("333K+");
}); });
