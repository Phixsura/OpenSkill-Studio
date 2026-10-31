import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiObservabilityV8Panel } from "@/components/fleet-ai-observability-v8-panel";
describe("FleetAiObservabilityV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiObservabilityV8Panel stacks={5} active={5} metrics={50000000000} traces={20000000000} logs={200000000000} />);
    expect(container.textContent).toContain("Observability v8");
}); });
