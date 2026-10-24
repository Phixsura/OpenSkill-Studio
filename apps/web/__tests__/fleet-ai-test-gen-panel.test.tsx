import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTestGenPanel } from "@/components/fleet-ai-test-gen-panel";
describe("FleetAiTestGenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTestGenPanel generators={4} active={4} tests={200000} coverageBoost={20} passRate={96} />);
    expect(container.textContent).toContain("Test Generation");
}); });
