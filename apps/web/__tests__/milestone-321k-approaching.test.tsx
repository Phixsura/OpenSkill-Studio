import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone321kApproaching } from "@/components/milestone-321k-approaching";
describe("Milestone321kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone321kApproaching />);
    expect(container.textContent).toContain("321K");
}); });
