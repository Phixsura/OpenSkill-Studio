import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSmokeTestPanel } from "@/components/fleet-ai-smoke-test-panel";
describe("FleetAiSmokeTestPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSmokeTestPanel testers={5} active={5} runs={5000} passRate={100} duration={5} />);
    expect(container.textContent).toContain("Smoke Test");
}); });
