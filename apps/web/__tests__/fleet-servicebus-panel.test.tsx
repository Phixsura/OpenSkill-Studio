import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServicebusPanel } from "@/components/fleet-servicebus-panel";
describe("FleetServicebusPanel", () => { it("renders", () => {
    const { container } = render(<FleetServicebusPanel namespaces={5} active={5} messages={5000000} dlqCount={10} />);
    expect(container.textContent).toContain("Service Bus");
    expect(container.textContent).toContain("10 DLQ");
}); });
