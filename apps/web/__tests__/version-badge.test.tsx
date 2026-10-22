import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionBadge } from "@/components/version-badge";

describe("VersionBadge", () => {
  it.each(["1.0.0", "2.3.4", "0.1.0-beta"])("renders version %s", (version) => {
    const { container } = render(<VersionBadge version={version} />);
    expect(container.textContent).toContain(version);
  });
});
