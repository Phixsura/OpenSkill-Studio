import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceAccountV9Panel } from "@/components/fleet-service-account-v9-panel";
describe("FleetServiceAccountV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceAccountV9Panel total={100} overPrivileged={0} />);
    expect(container.textContent).toContain("Service Account v9");
}); });
