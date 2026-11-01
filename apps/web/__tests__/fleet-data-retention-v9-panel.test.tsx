import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDataRetentionV9Panel } from "@/components/fleet-data-retention-v9-panel";
describe("FleetDataRetentionV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDataRetentionV9Panel policies={20} compliant={20} />);
    expect(container.textContent).toContain("Data Retention v9");
}); });
