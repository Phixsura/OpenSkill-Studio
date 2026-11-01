import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTfStatePanel } from "@/components/fleet-tf-state-panel";
describe("FleetTfStatePanel", () => { it("renders", () => {
    const { container } = render(<FleetTfStatePanel total={10} healthy={8} locked={1} failed={1} allOk={false} />);
    expect(container.textContent).toContain("Terraform State");
    expect(container.textContent).toContain("1 locked");
}); });
