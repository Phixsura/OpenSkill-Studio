import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAnthropicPanel } from "@/components/fleet-anthropic-panel";
describe("FleetAnthropicPanel", () => { it("renders", () => {
    const { container } = render(<FleetAnthropicPanel projects={5} active={5} requests={5000000} tokens={2000000000} />);
    expect(container.textContent).toContain("Anthropic");
}); });
