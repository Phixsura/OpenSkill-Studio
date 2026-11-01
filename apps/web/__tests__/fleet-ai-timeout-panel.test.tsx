import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTimeoutPanel } from "@/components/fleet-ai-timeout-panel";
describe("FleetAiTimeoutPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTimeoutPanel managers={4} active={4} timeouts={1000} defaultMs={30000} adaptive={3} />);
    expect(container.textContent).toContain("Timeout Manager");
}); });
