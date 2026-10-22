import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CodeBlock } from "@/components/code-block";

describe("CodeBlock", () => {
  it("shows code", () => {
    const { container } = render(<CodeBlock lines={["npm install @openskill/sdk", "echo hello"]} />);
    expect(container.textContent).toContain("npm install");
  });
  it("has copy button", () => {
    const { container } = render(<CodeBlock lines={["test"]} />);
    expect(container.textContent).toContain("Copy");
  });
});
