import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPosthogPanel } from "@/components/fleet-posthog-panel";
describe("FleetPosthogPanel", () => { it("renders", () => {
    const { container } = render(<FleetPosthogPanel instances={3} running={3} events={6000000} featureFlags={100} />);
    expect(container.textContent).toContain("PostHog");
    expect(container.textContent).toContain("100 flags");
}); });
