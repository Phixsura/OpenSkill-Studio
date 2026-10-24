import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetProgressiveDeliveryV9Panel } from "@/components/fleet-progressive-delivery-v9-panel";
describe("FleetProgressiveDeliveryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetProgressiveDeliveryV9Panel rollouts={50} inProgress={5} />);
    expect(container.textContent).toContain("Progressive Delivery v9");
}); });
