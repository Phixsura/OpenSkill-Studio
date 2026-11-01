import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOpsCenterPanel } from "@/components/fleet-ai-ops-center-panel";
describe("FleetAiOpsCenterPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiOpsCenterPanel centers={3} active={3} operators={100} alerts={500} actions={1000} regions={12} />);
    expect(container.textContent).toContain("Ops Center");
}); });
