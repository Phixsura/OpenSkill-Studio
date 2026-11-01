import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone302k } from "@/components/milestone-302k";
describe("Milestone302k", () => { it("renders", () => {
    const { container } = render(<Milestone302k />);
    expect(container.textContent).toContain("302K");
}); });
