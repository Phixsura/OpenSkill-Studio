import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CliToolCard } from "@/components/cli-tool-card";

const tool = {
  toolId: "ext-1:mycli", name: "mycli", version: "2.0", installCmd: "npm i -g mycli",
  commands: [
    { name: "init", description: "Initialize", usage: "mycli init [dir]" },
    { name: "build", description: "Build project", usage: "mycli build" },
  ],
};

describe("CliToolCard", () => {
  it("renders collapsed", () => {
    const { container } = render(<CliToolCard tool={tool} />);
    expect(container.textContent).toContain("mycli");
    expect(container.textContent).toContain("2 commands");
  });
  it("expands to show commands", () => {
    const { container } = render(<CliToolCard tool={tool} />);
    fireEvent.click(container.querySelector("button")!);
    expect(container.textContent).toContain("npm i -g mycli");
    expect(container.textContent).toContain("mycli init [dir]");
  });
});
