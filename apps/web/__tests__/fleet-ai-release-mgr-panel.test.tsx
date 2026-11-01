import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiReleaseMgrPanel } from "@/components/fleet-ai-release-mgr-panel";
describe("FleetAiReleaseMgrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiReleaseMgrPanel managers={3} active={3} releases={50} rollbacks={2} leadTime={10} />);
    expect(container.textContent).toContain("Release Manager");
}); });
