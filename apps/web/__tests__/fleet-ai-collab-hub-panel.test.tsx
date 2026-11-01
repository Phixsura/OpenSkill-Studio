import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCollabHubPanel } from "@/components/fleet-ai-collab-hub-panel";
describe("FleetAiCollabHubPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCollabHubPanel hubs={3} active={3} teams={100} sharedModels={1000} discussions={5000} />);
    expect(container.textContent).toContain("Collaboration Hub");
}); });
