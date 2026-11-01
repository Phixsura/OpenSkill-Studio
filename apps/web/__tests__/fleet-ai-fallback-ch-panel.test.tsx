import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFallbackChPanel } from "@/components/fleet-ai-fallback-ch-panel";
describe("FleetAiFallbackChPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiFallbackChPanel chains={4} active={4} fallbacks={20000} models={8} successRate={99.95} />);
    expect(container.textContent).toContain("Fallback Chain");
}); });
