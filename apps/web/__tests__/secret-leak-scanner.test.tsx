import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SecretLeakScanner } from "@/components/secret-leak-scanner";

describe("SecretLeakScanner", () => {
  it("renders", () => {
    const { container } = render(
      <SecretLeakScanner filesScanned={50} cleanFiles={48} totalFindings={3} pass={false}
        findings={[
          { type: "api_key", severity: "medium", file: "config.py", matchPreview: "sk_live_abc..." },
          { type: "password", severity: "high", file: ".env", matchPreview: "password=sec..." },
        ]} />
    );
    expect(container.textContent).toContain("Secret Scanner");
    expect(container.textContent).toContain("3 secrets found");
    expect(container.textContent).toContain("50 files");
    expect(container.textContent).toContain("api_key");
    expect(container.textContent).toContain("config.py");
  });
});
