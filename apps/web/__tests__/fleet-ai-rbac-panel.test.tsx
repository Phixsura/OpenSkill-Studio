import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRbacPanel } from "@/components/fleet-ai-rbac-panel";
describe("FleetAiRbacPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRbacPanel engines={3} active={3} roles={100} policies={500} evals={500000000} />);
    expect(container.textContent).toContain("AI RBAC");
}); });
