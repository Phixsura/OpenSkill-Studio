import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCircuitBrkPanel } from "@/components/fleet-ai-circuit-brk-panel";
describe("FleetAiCircuitBrkPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCircuitBrkPanel breakers={10} closed={10} halfOpen={0} open={0} trips={3} />);
    expect(container.textContent).toContain("Circuit Breaker");
}); });
