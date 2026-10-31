import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FileTreeView } from "@/components/file-tree-view";

describe("FileTreeView", () => {
  const tree = {
    src: {
      "index.ts": { type: "file", icon: "📄" },
      components: {
        "Button.tsx": { type: "file", icon: "⚛️" },
      },
    },
    "package.json": { type: "file", icon: "📋" },
  };
  it("renders", () => {
    const { container } = render(<FileTreeView tree={tree} />);
    expect(container.textContent).toContain("src");
    expect(container.textContent).toContain("index.ts");
    expect(container.textContent).toContain("📄");
    expect(container.textContent).toContain("package.json");
    expect(container.textContent).toContain("📋");
  });
});
