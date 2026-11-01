import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudInventoryV9Panel } from "@/components/fleet-cloud-inventory-v9-panel";
describe("FleetCloudInventoryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCloudInventoryV9Panel resources={5000} types={50} />);
    expect(container.textContent).toContain("Cloud Inventory v9");
}); });
