import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCodeReviewV9Panel } from "@/components/fleet-code-review-v9-panel";
describe("FleetCodeReviewV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCodeReviewV9Panel total={500} avgHours={2} />);
    expect(container.textContent).toContain("Code Review v9");
}); });
