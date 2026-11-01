import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRlV4Panel } from "@/components/fleet-ai-rl-v4-panel";
describe("FleetAiRlV4Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiRlV4Panel limiters={5} active={5} rules={1000} throttled={50000} adaptive={true} />);
    expect(container.textContent).toContain("Rate Limiter v4");
}); });
