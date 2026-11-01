import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSafetyPanel } from "@/components/fleet-ai-safety-panel";
describe("FleetAiSafetyPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSafetyPanel monitors={10} active={10} violations={0} checks={5000000} />);
    expect(container.textContent).toContain("AI Safety");
}); });
