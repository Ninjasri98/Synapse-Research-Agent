import type { Metadata } from "next";
import { Oxanium } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";

const oxanium = Oxanium({
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000"
  ),
  title: {
    default:
      "Synpase - AI-Powered Research Assistant | Transform Your Research Process",
    template: "%s | Synpase",
  },
  description:
    "Transform your research with Synapse's AI-powered platform. Upload documents, analyze URLs, generate summaries, create interactive Q&A, audio overviews, visual mindmaps, and FAQs. Bypass geo-restrictions with Bright Data integration.",
  
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${oxanium.className} antialiased`}>
        <Header />
        <main className="min-h-screen pt-4">{children}</main>
        <Footer />
        <Toaster />
      </body>
    </html>
  );
}
