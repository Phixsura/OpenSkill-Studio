import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCodeReviewPanel } from "@/components/fleet-code-review-panel";
describe("FleetCodeReviewPanel", () => { it("renders", () => {
    const { container } = render(<FleetCodeReviewPanel totalPrs={20} reviewed={18} unreviewed={2} avgReviewHours={6} fast={true} />);
    expect(container.textContent).toContain("Code Review");
    expect(container.textContent).toContain("2 unreviewed");
}); });
