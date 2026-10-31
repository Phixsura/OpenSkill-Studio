import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGitopsSyncV9Panel } from "@/components/fleet-gitops-sync-v9-panel";
describe("FleetGitopsSyncV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetGitopsSyncV9Panel repos={20} synced={20} />);
    expect(container.textContent).toContain("GitOps Sync v9");
}); });
