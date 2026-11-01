import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDesignReviewV9Panel } from "@/components/fleet-api-design-review-v9-panel";
describe("FleetApiDesignReviewV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiDesignReviewV9Panel reviews={50} approved={45} />);
    expect(container.textContent).toContain("API Design Review v9");
}); });
