import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiChangelogPanel } from "@/components/fleet-ai-changelog-panel";
describe("FleetAiChangelogPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiChangelogPanel changelogs={2} active={2} releases={200} features={1000} fixes={600} subscribers={50000} />);
    expect(container.textContent).toContain("AI Changelog");
}); });
