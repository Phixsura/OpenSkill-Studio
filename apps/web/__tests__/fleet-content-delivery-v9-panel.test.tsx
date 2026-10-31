import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetContentDeliveryV9Panel } from "@/components/fleet-content-delivery-v9-panel";
describe("FleetContentDeliveryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetContentDeliveryV9Panel assets={1000} saved={500} />);
    expect(container.textContent).toContain("Content Delivery v9");
}); });
