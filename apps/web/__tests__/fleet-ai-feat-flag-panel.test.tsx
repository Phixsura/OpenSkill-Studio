import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFeatFlagPanel } from "@/components/fleet-ai-feat-flag-panel";
describe("FleetAiFeatFlagPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiFeatFlagPanel systems={3} active={3} flags={500} enabled={350} evaluations={500000000} />);
    expect(container.textContent).toContain("Feature Flags");
}); });
