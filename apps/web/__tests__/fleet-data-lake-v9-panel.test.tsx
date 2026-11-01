import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDataLakeV9Panel } from "@/components/fleet-data-lake-v9-panel";
describe("FleetDataLakeV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDataLakeV9Panel partitions={200} sizeTb={500} />);
    expect(container.textContent).toContain("Data Lake v9");
}); });
