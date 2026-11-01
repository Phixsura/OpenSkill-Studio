import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone308k } from "@/components/milestone-308k";
describe("Milestone308k", () => { it("renders", () => {
    const { container } = render(<Milestone308k />);
    expect(container.textContent).toContain("308K");
}); });
