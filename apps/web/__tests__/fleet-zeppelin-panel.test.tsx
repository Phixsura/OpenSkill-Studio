import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetZeppelinPanel } from "@/components/fleet-zeppelin-panel";
describe("FleetZeppelinPanel", () => { it("renders", () => {
    const { container } = render(<FleetZeppelinPanel instances={5} running={5} notebooks={500} interpreters={20} />);
    expect(container.textContent).toContain("Zeppelin");
}); });
