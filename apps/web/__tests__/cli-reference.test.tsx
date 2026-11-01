import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CliReference } from "@/components/cli-reference";

describe("CliReference", () => {
  const commands = [
    { command: "init", description: "Initialize app", usage: "osk init <name>", flagCount: 3 },
    { command: "deploy", description: "Deploy app", usage: "osk deploy", flagCount: 3 },
  ];
  it("renders commands", () => {
    const { container } = render(<CliReference commands={commands} />);
    expect(container.textContent).toContain("osk init");
    expect(container.textContent).toContain("osk deploy");
    expect(container.textContent).toContain("Initialize app");
    expect(container.textContent).toContain("3 flags");
  });
});
