import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSandboxPanel } from "@/components/fleet-ai-sandbox-panel";
describe("FleetAiSandboxPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSandboxPanel sandboxes={10} running={10} executions={2000000} isolated={10} />);
    expect(container.textContent).toContain("AI Sandbox");
}); });
