import { Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

interface DonationButtonProps {
  variant?: "default" | "outline" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
  className?: string;
  showIcon?: boolean;
  children?: React.ReactNode;
}

export function DonationButton({
  variant = "default",
  size = "default",
  className = "",
  showIcon = false,
  children,
}: DonationButtonProps) {
  const donationUrl =
    "";

  return (
    <Button
      variant={variant}
      size={size}
      className={`bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg hover:shadow-xl transition-all duration-300 ${className}`}
      asChild
    >
      <Link
        href={donationUrl}
        target="_blank"
        rel="noopener noreferrer"
        data-umami-event="frontend_donation_click"
        data-umami-event-section="donation_button"
      >
        {showIcon && <Heart className="h-4 w-4 mr-2" />}
        {children || "Support Us"}
      </Link>
    </Button>
  );
}
