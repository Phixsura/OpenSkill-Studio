import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeepnotePanel } from "@/components/fleet-deepnote-panel";
describe("FleetDeepnotePanel", () => { it("renders", () => {
    const { container } = render(<FleetDeepnotePanel workspaces={5} active={5} projects={200} integrations={30} />);
    expect(container.textContent).toContain("Deepnote");
}); });
