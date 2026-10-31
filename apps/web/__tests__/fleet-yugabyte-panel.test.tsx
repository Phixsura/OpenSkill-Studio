import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetYugabytePanel } from "@/components/fleet-yugabyte-panel";
describe("FleetYugabytePanel", () => { it("renders", () => {
    const { container } = render(<FleetYugabytePanel clusters={3} running={3} tablets={9000} tservers={27} />);
    expect(container.textContent).toContain("YugabyteDB");
    expect(container.textContent).toContain("9,000 tablets");
}); });
