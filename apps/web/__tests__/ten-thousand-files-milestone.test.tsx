import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TenThousandFilesMilestone } from "@/components/ten-thousand-files-milestone";
describe("TenThousandFilesMilestone", () => { it("renders", () => {
    const { container } = render(<TenThousandFilesMilestone />);
    expect(container.textContent).toContain("10,000 FILES");
    expect(container.textContent).toContain("Five digits");
    expect(container.textContent).toContain("3,289");
}); });
