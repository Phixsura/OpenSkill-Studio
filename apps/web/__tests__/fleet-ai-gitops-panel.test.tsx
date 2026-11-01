import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGitopsPanel } from "@/components/fleet-ai-gitops-panel";
describe("FleetAiGitopsPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiGitopsPanel controllers={4} active={4} repos={200} syncs={1000} outOfSync={0} />);
    expect(container.textContent).toContain("AI GitOps");
}); });
