import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWfDagPanel } from "@/components/fleet-ai-wf-dag-panel";
describe("FleetAiWfDagPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiWfDagPanel engines={3} active={3} dags={50000} nodes={2500000} parallelism={12} />);
    expect(container.textContent).toContain("Workflow DAG");
}); });
