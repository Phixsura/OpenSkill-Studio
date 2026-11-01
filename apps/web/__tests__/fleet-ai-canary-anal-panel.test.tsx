import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCanaryAnalPanel } from "@/components/fleet-ai-canary-anal-panel";
describe("FleetAiCanaryAnalPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCanaryAnalPanel analyzers={4} active={4} analyses={100} promoted={95} rolledBack={0} />);
    expect(container.textContent).toContain("Canary Analysis");
}); });
