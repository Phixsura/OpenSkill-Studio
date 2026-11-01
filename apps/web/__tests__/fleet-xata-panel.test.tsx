import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetXataPanel } from "@/components/fleet-xata-panel";
describe("FleetXataPanel", () => { it("renders", () => {
    const { container } = render(<FleetXataPanel databases={5} active={5} branches={15} records={5000000} />);
    expect(container.textContent).toContain("Xata");
}); });
