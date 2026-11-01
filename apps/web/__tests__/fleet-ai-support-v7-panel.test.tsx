import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSupportV7Panel } from "@/components/fleet-ai-support-v7-panel";
describe("FleetAiSupportV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiSupportV7Panel systems={3} active={3} tickets={20000} res={5} csat={4.9} auto={18000} />);
    expect(container.textContent).toContain("Support v7");
}); });
