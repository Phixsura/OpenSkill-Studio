import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGitopsPanel } from "@/components/fleet-gitops-panel";
describe("FleetGitopsPanel", () => { it("renders", () => {
    const { container } = render(<FleetGitopsPanel total={10} synced={8} outOfSync={2} allSynced={false} />);
    expect(container.textContent).toContain("GitOps Sync");
    expect(container.textContent).toContain("2 out of sync");
}); });
