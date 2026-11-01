import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetConcoursePanel } from "@/components/fleet-concourse-panel";
describe("FleetConcoursePanel", () => { it("renders", () => {
    const { container } = render(<FleetConcoursePanel pipelines={15} paused={2} jobsPassing={50} jobsFailing={3} />);
    expect(container.textContent).toContain("Concourse");
}); });
