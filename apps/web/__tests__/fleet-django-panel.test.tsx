import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDjangoPanel } from "@/components/fleet-django-panel";
describe("FleetDjangoPanel", () => { it("renders", () => {
    const { container } = render(<FleetDjangoPanel apps={5} running={5} views={500} pendingMigrations={0} />);
    expect(container.textContent).toContain("Django");
    expect(container.textContent).toContain("500 views");
}); });
