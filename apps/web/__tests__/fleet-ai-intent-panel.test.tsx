import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiIntentPanel } from "@/components/fleet-ai-intent-panel";
describe("FleetAiIntentPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiIntentPanel services={5} active={5} classifications={25000000} intents={500} />);
    expect(container.textContent).toContain("AI Intent");
}); });
