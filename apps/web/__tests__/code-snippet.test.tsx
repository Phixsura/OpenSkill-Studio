import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CodeSnippet } from "@/components/code-snippet";

describe("CodeSnippet", () => {
  const lines = [{ number: 1, content: "def hello():" }, { number: 2, content: "    print('hi')" }];
  it("renders code with line numbers", () => {
    const { container } = render(
      <CodeSnippet language="python" icon="🐍" title="example.py" lines={lines} showLineNumbers={true} />
    );
    expect(container.textContent).toContain("example.py");
    expect(container.textContent).toContain("python");
    expect(container.textContent).toContain("def hello():");
    expect(container.textContent).toContain("1");
    expect(container.textContent).toContain("Copy");
  });
});
