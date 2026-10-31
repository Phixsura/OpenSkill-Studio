import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSentryPanel } from "@/components/fleet-sentry-panel";
describe("FleetSentryPanel", () => { it("renders", () => {
    const { container } = render(<FleetSentryPanel projects={20} events={10000} unresolved={15} crashFree={99.5} />);
    expect(container.textContent).toContain("Sentry");
    expect(container.textContent).toContain("15 unresolved");
}); });
