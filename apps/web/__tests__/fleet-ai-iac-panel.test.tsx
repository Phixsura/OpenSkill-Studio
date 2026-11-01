import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiIacPanel } from "@/components/fleet-ai-iac-panel";
describe("FleetAiIacPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiIacPanel systems={3} active={3} resources={10000} applies={100} driftFree={99.5} />);
    expect(container.textContent).toContain("Infra as Code");
}); });
