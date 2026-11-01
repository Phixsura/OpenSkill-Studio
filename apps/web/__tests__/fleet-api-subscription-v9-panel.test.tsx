import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiSubscriptionV9Panel } from "@/components/fleet-api-subscription-v9-panel";
describe("FleetApiSubscriptionV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiSubscriptionV9Panel subs={100} events={100000} />);
    expect(container.textContent).toContain("API Subscription v9");
}); });
