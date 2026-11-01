import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelTestPanel } from "@/components/fleet-ai-model-test-panel";
describe("FleetAiModelTestPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelTestPanel testers={4} active={4} tests={500000} passed={498000} failed={2000} passRate={99.6} />);
    expect(container.textContent).toContain("Model Testing");
}); });
