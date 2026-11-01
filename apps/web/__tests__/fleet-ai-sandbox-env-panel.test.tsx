import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSandboxEnvPanel } from "@/components/fleet-ai-sandbox-env-panel";
describe("FleetAiSandboxEnvPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSandboxEnvPanel envs={4} active={4} environments={500} sessions={20000} lifetime={6} />);
    expect(container.textContent).toContain("Sandbox Env");
}); });
