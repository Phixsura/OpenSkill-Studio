import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMongodbPanel } from "@/components/fleet-mongodb-panel";
describe("FleetMongodbPanel", () => { it("renders", () => {
    const { container } = render(<FleetMongodbPanel members={3} primary={1} secondary={2} maxLag={1} healthy={true} />);
    expect(container.textContent).toContain("MongoDB");
    expect(container.textContent).toContain("1P/2S");
}); });
