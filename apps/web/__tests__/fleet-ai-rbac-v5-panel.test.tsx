import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRbacV5Panel } from "@/components/fleet-ai-rbac-v5-panel";
describe("FleetAiRbacV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiRbacV5Panel engines={4} active={4} roles={500} permissions={5000} evals={5000000000} />);
    expect(container.textContent).toContain("AI RBAC v5");
}); });
