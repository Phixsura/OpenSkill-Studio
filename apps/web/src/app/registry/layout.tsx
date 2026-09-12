// R193 (Lighthouse a11y: landmark-one-main): the public registry rendered
// into the root layout's bare children — the only section without a <main>
// landmark, so screen-reader users had no skip-to-content target here
// (dashboard, client portal, and public profiles all carry one).
export default function RegistryLayout({ children }: { children: React.ReactNode }) {
  return <main id="main-content">{children}</main>;
}
