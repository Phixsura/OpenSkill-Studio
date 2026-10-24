import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiConfigMgrPanel } from "@/components/fleet-ai-config-mgr-panel";
describe("FleetAiConfigMgrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiConfigMgrPanel managers={3} active={3} configs={1000} versions={5000} rollbacks={0} />);
    expect(container.textContent).toContain("Config Manager");
}); });
