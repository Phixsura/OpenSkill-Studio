import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SdkInstallCard } from "@/components/sdk-install-card";

describe("SdkInstallCard", () => {
  const sdks = [
    { language: "typescript", latest: "3.2.0", install: "npm install @openskill/sdk" },
    { language: "python", latest: "2.1.0", install: "pip install openskill-sdk" },
  ];
  it("renders SDK options", () => {
    const { container } = render(<SdkInstallCard sdks={sdks} />);
    expect(container.textContent).toContain("Install SDK");
    expect(container.textContent).toContain("typescript");
    expect(container.textContent).toContain("python");
    expect(container.textContent).toContain("npm install");
    expect(container.textContent).toContain("v3.2.0");
  });
});
