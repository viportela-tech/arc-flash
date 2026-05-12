import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "ArcFlash MVP",
  description: "Ferramenta web para estudos de arc flash"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
