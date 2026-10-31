import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LockfileViewer } from "@/components/lockfile-viewer";

const deps = [
  { name: "react", version: "18.2.0", integrity: "abc12345" },
  { name: "axios", version: "1.4.0", integrity: "def67890" },
];
const diff = { added: { "lodash": "4.17.0" }, removed: {}, changed: { "react": { from: "17.0.0", to: "18.2.0" } } };

describe("LockfileViewer", () => {
  it("renders deps", () => {
    const { container } = render(<LockfileViewer deps={deps} />);
    expect(container.textContent).toContain("react");
    expect(container.textContent).toContain("18.2.0");
    expect(container.textContent).toContain("2 packages");
  });
  it("renders diff", () => {
    const { container } = render(<LockfileViewer deps={deps} diff={diff} />);
    expect(container.textContent).toContain("+ lodash@4.17.0");
    expect(container.textContent).toContain("~ react 17.0.0 → 18.2.0");
  });
});
