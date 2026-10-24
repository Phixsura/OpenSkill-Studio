import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetJenkinsPanel } from "@/components/fleet-jenkins-panel";
describe("FleetJenkinsPanel", () => { it("renders", () => {
    const { container } = render(<FleetJenkinsPanel controllers={2} online={2} agents={40} queueSize={5} />);
    expect(container.textContent).toContain("Jenkins");
    expect(container.textContent).toContain("40 agents");
}); });
