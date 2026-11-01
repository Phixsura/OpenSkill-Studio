import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRabbitmqPanel } from "@/components/fleet-rabbitmq-panel";
describe("FleetRabbitmqPanel", () => { it("renders", () => {
    const { container } = render(<FleetRabbitmqPanel nodes={3} running={3} queues={80} messages={15000} healthy={true} />);
    expect(container.textContent).toContain("RabbitMQ");
    expect(container.textContent).toContain("15,000 msgs");
}); });
