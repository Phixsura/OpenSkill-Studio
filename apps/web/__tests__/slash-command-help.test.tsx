import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlashCommandHelp } from "@/components/slash-command-help";

describe("SlashCommandHelp", () => {
  const commands = [
    { command: "/status", description: "Check status", usage: "/status [app]" },
    { command: "/deploy", description: "Deploy app", usage: "/deploy <app> <ver>" },
  ];
  it("renders commands", () => {
    const { container } = render(<SlashCommandHelp commands={commands} />);
    expect(container.textContent).toContain("/status");
    expect(container.textContent).toContain("/deploy");
    expect(container.textContent).toContain("Check status");
    expect(container.textContent).toContain("/deploy <app> <ver>");
  });
});
