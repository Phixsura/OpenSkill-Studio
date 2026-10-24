import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetInngestPanel } from "@/components/fleet-inngest-panel";
describe("FleetInngestPanel", () => { it("renders", () => {
    const { container } = render(<FleetInngestPanel apps={5} active={5} functions={100} events={500000} />);
    expect(container.textContent).toContain("Inngest");
}); });
