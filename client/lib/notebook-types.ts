import {
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";

export const statusConfig = {
  IN_QUEUE: {
    icon: Clock,
    label: "In Queue",
    variant: "secondary" as const,
  },
  IN_PROGRESS: {
    icon: Loader2,
    label: "Processing",
    variant: "default" as const,
  },
  PROCESSED: {
    icon: CheckCircle2,
    label: "Processed",
    variant: "secondary" as const,
  },
  ERROR: {
    icon: AlertCircle,
    label: "Error",
    variant: "destructive" as const,
  },
};

// Type for notebook document source type
export type NotebookDocumentSourceType = "UPLOAD" | "URL" | "MANUAL";

// Define type for notebook with its relations
export type NotebookWithDetails = {
  id: string;
  title: string | null;
  topic: string | null;
  userId: string;
  createdAt: Date;
  updatedAt: Date | null;
  processingStatus?: {
    id: string;
    status: string;
    message: string | null;
    createdAt: Date;
    updatedAt: Date | null;
    notebookId: string;
  } | null;
  sources: Array<{
    id: string;
    createdAt: Date;
    notebookId: string;
    sourceType: NotebookDocumentSourceType;
    sourceUrl: string | null;
    sourceUrlText: string | null;
    filePath: string | null;
    filename: string | null;
    content: string | null;
    updatedAt?: Date | null;
    title?: string | null;
  }>;
  output?: {
    id: string;
    summary: string | null;
    audioOverviewUrl: string | null;
    mindmap: string | null;
    notebookId: string;
    createdAt: Date;
    updatedAt: Date | null;
    faqs: Array<{
      id: string;
      question: string;
      answer: string;
      createdAt: Date;
      updatedAt: Date | null;
    }>;
  } | null;
};