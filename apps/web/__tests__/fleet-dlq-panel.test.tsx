import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDlqPanel } from "@/components/fleet-dlq-panel";
describe("FleetDlqPanel", () => { it("renders", () => {
    const { container } = render(<FleetDlqPanel queues={5} totalMessages={150} nonEmpty={2} clean={false} />);
    expect(container.textContent).toContain("Dead Letter Queues");
    expect(container.textContent).toContain("150 msgs");
}); });
