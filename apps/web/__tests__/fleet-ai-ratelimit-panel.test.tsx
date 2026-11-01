import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRatelimitPanel } from "@/components/fleet-ai-ratelimit-panel";
describe("FleetAiRatelimitPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRatelimitPanel configs={10} active={10} throttled={5000} requests={5000000} />);
    expect(container.textContent).toContain("AI Rate Limit");
}); });
