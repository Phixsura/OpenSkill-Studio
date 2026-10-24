import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSagaOrchPanel } from "@/components/fleet-ai-saga-orch-panel";
describe("FleetAiSagaOrchPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSagaOrchPanel orchestrators={3} active={3} sagas={500000} completed={495000} compensated={5000} />);
    expect(container.textContent).toContain("Saga Orchestrator");
}); });
