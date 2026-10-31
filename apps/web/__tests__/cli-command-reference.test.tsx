import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CliCommandReference } from "@/components/cli-command-reference";

describe("CliCommandReference", () => {
  const commands = [
    { name: "init", description: "Initialize", args: [{ name: "template", type: "string", required: true, description: "Template name" }] },
    { name: "deploy", description: "Deploy app", args: [] },
  ];
  it("renders", () => {
    const { container } = render(
      <CliCommandReference cliName="myapp" commands={commands} installCmd="npm install -g @openskill/myapp-cli" />
    );
    expect(container.textContent).toContain("CLI Reference");
    expect(container.textContent).toContain("npm install");
    expect(container.textContent).toContain("myapp init");
    expect(container.textContent).toContain("myapp deploy");
    expect(container.textContent).toContain("template");
    expect(container.textContent).toContain("required");
  });
});
