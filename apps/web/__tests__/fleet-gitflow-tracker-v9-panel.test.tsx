import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGitflowTrackerV9Panel } from "@/components/fleet-gitflow-tracker-v9-panel";
describe("FleetGitflowTrackerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetGitflowTrackerV9Panel repos={20} openPrs={50} />);
    expect(container.textContent).toContain("Gitflow Tracker v9");
}); });
