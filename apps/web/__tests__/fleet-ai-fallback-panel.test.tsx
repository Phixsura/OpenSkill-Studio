import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFallbackPanel } from "@/components/fleet-ai-fallback-panel";
describe("FleetAiFallbackPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiFallbackPanel chains={5} active={5} fallbacks={2000} primarySuccess={97} />);
    expect(container.textContent).toContain("AI Fallback");
}); });
