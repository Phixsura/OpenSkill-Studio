import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGitlabCiPanel } from "@/components/fleet-gitlab-ci-panel";
describe("FleetGitlabCiPanel", () => { it("renders", () => {
    const { container } = render(<FleetGitlabCiPanel total={50} success={45} failed={5} avgDuration={10} />);
    expect(container.textContent).toContain("GitLab CI");
}); });
