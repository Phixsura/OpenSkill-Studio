import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKafkaPanel } from "@/components/fleet-kafka-panel";
describe("FleetKafkaPanel", () => { it("renders", () => {
    const { container } = render(<FleetKafkaPanel brokers={6} online={6} underReplicated={0} totalTopics={100} healthy={true} />);
    expect(container.textContent).toContain("Kafka");
    expect(container.textContent).toContain("100 topics");
}); });
