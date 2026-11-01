import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiIntegTestPanel } from "@/components/fleet-ai-integ-test-panel";
describe("FleetAiIntegTestPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiIntegTestPanel testers={4} active={4} suites={100} tests={50000} passRate={99.5} />);
    expect(container.textContent).toContain("Integration Test");
}); });
