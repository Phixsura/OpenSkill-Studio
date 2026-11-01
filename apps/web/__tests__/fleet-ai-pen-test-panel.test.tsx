import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPenTestPanel } from "@/components/fleet-ai-pen-test-panel";
describe("FleetAiPenTestPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPenTestPanel testers={3} active={3} tests={1000} findings={25} critical={0} />);
    expect(container.textContent).toContain("Pen Testing");
}); });
