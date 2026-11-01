import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGitopsMatPanel } from "@/components/fleet-gitops-mat-panel";
describe("FleetGitopsMatPanel", () => { it("renders", () => {
    const { container } = render(<FleetGitopsMatPanel score={85} level="Level 3" />);
    expect(container.textContent).toContain("GitOps Maturity");
    expect(container.textContent).toContain("85 — Level 3");
}); });
