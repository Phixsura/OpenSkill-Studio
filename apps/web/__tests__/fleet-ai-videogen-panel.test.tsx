import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiVideogenPanel } from "@/components/fleet-ai-videogen-panel";
describe("FleetAiVideogenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiVideogenPanel services={3} active={3} videos={150000} minutes={300000} />);
    expect(container.textContent).toContain("AI Video Gen");
}); });
