import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlaygroundOutput } from "@/components/playground-output";

describe("PlaygroundOutput", () => {
  it("renders success output", () => {
    const { container } = render(
      <PlaygroundOutput stdout="Hello World" stderr="" exitCode={0} success={true} executionMs={42} />
    );
    expect(container.textContent).toContain("Hello World");
    expect(container.textContent).toContain("exit 0");
    expect(container.textContent).toContain("42ms");
  });
  it("renders error output", () => {
    const { container } = render(
      <PlaygroundOutput stdout="" stderr="NameError: x" exitCode={1} success={false} executionMs={10} />
    );
    expect(container.textContent).toContain("NameError");
    expect(container.textContent).toContain("exit 1");
  });
});
