import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CliReferencePage } from "@/components/cli-reference-page";

describe("CliReferencePage", () => {
  it("renders", () => {
    const groups = { apps: { deploy: { description: "Deploy app", flags: ["--env"] } } };
    const { container } = render(<CliReferencePage groups={groups} />);
    expect(container.textContent).toContain("CLI Reference");
    expect(container.textContent).toContain("openskill apps deploy");
    expect(container.textContent).toContain("--env");
  });
});
