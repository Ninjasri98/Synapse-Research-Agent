"use client";

import { useCallback, useState } from "react";
import { Upload, FileText, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface UploadedFile {
  filePath: string;
  filename: string;
  fileSize: number;
  fileType: string;
  publicUrl: string;
}

interface FileUploadProps {
  onFileUpload: (result: UploadedFile) => void;
  onError: (error: string) => void;
  disabled?: boolean;
  maxSizeInMB?: number;
  acceptedTypes?: string[];
  className?: string;
  multiple?: boolean;
}

export function FileUpload({
  onFileUpload,
  onError,
  disabled = false,
  maxSizeInMB = 10,
  acceptedTypes = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  ],
  className,
  multiple = true,
}: FileUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<string[]>([]);

  const getFileTypeNames = (types: string[]): string[] => {
    const typeMap: Record<string, string> = {
      "application/pdf": "PDF",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        "DOCX",
      "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        "PPTX",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        "XLSX",
    };

    return types.map((type) => typeMap[type] || type);
  };

  const validateFile = useCallback(
    (file: File): string | null => {
      if (!acceptedTypes.includes(file.type)) {
        return `File type not supported. Please upload: ${getFileTypeNames(
          acceptedTypes
        ).join(", ")}`;
      }

      if (file.size > maxSizeInMB * 1024 * 1024) {
        return `File size exceeds ${maxSizeInMB}MB limit`;
      }

      return null;
    },
    [acceptedTypes, maxSizeInMB]
  );

  const uploadFile = useCallback(
    async (file: File) => {
      setUploadingFiles((prev) => [...prev, file.name]);

      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("/api/upload", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Upload failed");
        }

        const result = await response.json();
        onFileUpload(result);
      } catch (error) {
        onError(error instanceof Error ? error.message : "Upload failed");
      } finally {
        setUploadingFiles((prev) => prev.filter((name) => name !== file.name));
      }
    },
    [onFileUpload, onError]
  );

  const uploadFiles = useCallback(
    async (files: File[]) => {
      setIsUploading(true);

      try {
        // Upload files sequentially to avoid overwhelming the server
        for (const file of files) {
          await uploadFile(file);
        }
      } finally {
        setIsUploading(false);
      }
    },
    [uploadFile]
  );

  const handleFileSelect = useCallback(
    (files: FileList | null) => {
      if (!files || files.length === 0) return;

      const fileArray = Array.from(files);
      const validFiles: File[] = [];

      // Validate all files first
      for (const file of fileArray) {
        const error = validateFile(file);
        if (error) {
          onError(error);
          return;
        }
        validFiles.push(file);
      }

      if (validFiles.length > 0) {
        uploadFiles(validFiles);
      }
    },
    [validateFile, onError, uploadFiles]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);

      if (disabled || isUploading) return;

      handleFileSelect(e.dataTransfer.files);
    },
    [disabled, isUploading, handleFileSelect]
  );

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      if (!disabled && !isUploading) {
        setIsDragOver(true);
      }
    },
    [disabled, isUploading]
  );

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const triggerFileSelect = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.multiple = multiple;
    input.accept = acceptedTypes.join(",");
    input.onchange = (e) => {
      const target = e.target as HTMLInputElement;
      handleFileSelect(target.files);
    };
    input.click();
  };

  return (
    <div className="space-y-3">
      <div
        className={cn(
          "relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ease-in-out",
          "hover:border-primary/50 hover:bg-primary/5",
          isDragOver
            ? "border-primary bg-primary/10 scale-[1.02]"
            : "border-muted-foreground/25",
          disabled && "opacity-50 cursor-not-allowed",
          isUploading && "pointer-events-none",
          className
        )}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="space-y-4">
          {isUploading ? (
            <>
              <div className="mx-auto h-12 w-12 text-primary animate-bounce">
                <Upload className="h-full w-full" />
              </div>
              <div>
                <p className="text-sm font-medium text-primary">
                  Uploading{" "}
                  {uploadingFiles.length > 0
                    ? `${uploadingFiles.length} file${
                        uploadingFiles.length > 1 ? "s" : ""
                      }`
                    : "files"}
                  ...
                </p>
                {uploadingFiles.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {uploadingFiles.map((filename, index) => (
                      <p key={index} className="text-xs text-muted-foreground">
                        {filename}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <div className="mx-auto h-12 w-12 text-muted-foreground/60">
                <FileText className="h-full w-full" />
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium text-foreground">
                  Drag and drop {multiple ? "files" : "a file"} here
                </p>
                <p className="text-xs text-muted-foreground">
                  or click to browse your computer
                </p>
                <p className="text-xs text-muted-foreground">
                  Supports: {getFileTypeNames(acceptedTypes).join(", ")} • Max{" "}
                  {maxSizeInMB}MB each
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                type="button"
                disabled={disabled}
                onClick={triggerFileSelect}
                className="mt-4 hover:bg-primary/10 hover:border-primary/50 transition-colors"
              >
                <Plus className="mr-2 h-4 w-4" />
                {multiple ? "Choose Files" : "Choose File"}
              </Button>
            </>
          )}
        </div>

        {/* Overlay effect when dragging */}
        {isDragOver && (
          <div className="absolute inset-0 bg-primary/10 border-2 border-primary border-dashed rounded-xl flex items-center justify-center">
            <div className="text-primary font-medium">
              Drop {multiple ? "files" : "file"} here
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
