import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEventbridgePanel } from "@/components/fleet-eventbridge-panel";
describe("FleetEventbridgePanel", () => { it("renders", () => {
    const { container } = render(<FleetEventbridgePanel buses={5} events={10000000} rules={100} failedInvocations={0} />);
    expect(container.textContent).toContain("EventBridge");
    expect(container.textContent).toContain("10,000,000");
}); });
