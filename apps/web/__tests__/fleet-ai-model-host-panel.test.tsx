import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelHostPanel } from "@/components/fleet-ai-model-host-panel";
describe("FleetAiModelHostPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelHostPanel hosts={5} active={5} models={1000} endpoints={2000} uptime={99.999} />);
    expect(container.textContent).toContain("Model Hosting");
}); });
