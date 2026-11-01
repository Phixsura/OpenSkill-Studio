import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Platform3010KMilestone } from "@/components/platform-3010k-milestone";
describe("Platform3010KMilestone", () => { it("renders", () => {
    const { container } = render(<Platform3010KMilestone />);
    expect(container.textContent).toContain("3,010,000");
    expect(container.textContent).toContain("9.94x");
}); });
