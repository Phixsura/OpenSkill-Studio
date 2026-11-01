import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDlqPanel } from "@/components/fleet-ai-dlq-panel";
describe("FleetAiDlqPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDlqPanel queues={4} active={4} messages={100} retried={90} discarded={10} />);
    expect(container.textContent).toContain("Dead Letter Queue");
}); });
