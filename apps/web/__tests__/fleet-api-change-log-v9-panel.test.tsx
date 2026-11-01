import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiChangeLogV9Panel } from "@/components/fleet-api-change-log-v9-panel";
describe("FleetApiChangeLogV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiChangeLogV9Panel changes={50} breaking={0} />);
    expect(container.textContent).toContain("API Change Log v9");
}); });
