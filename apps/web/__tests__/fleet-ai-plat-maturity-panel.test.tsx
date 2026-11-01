import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatMaturityPanel } from "@/components/fleet-ai-plat-maturity-panel";
describe("FleetAiPlatMaturityPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatMaturityPanel assessors={3} active={3} level={5} dimensions={25} score={98} />);
    expect(container.textContent).toContain("Platform Maturity");
}); });
