import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOpenSSFPanel } from "@/components/fleet-openssf-panel";
describe("FleetOpenSSFPanel", () => { it("renders", () => {
    const { container } = render(<FleetOpenSSFPanel total={20} avgScore={7.5} lowScore={2} grade="B" />);
    expect(container.textContent).toContain("OpenSSF");
    expect(container.textContent).toContain("7.5/10");
}); });
