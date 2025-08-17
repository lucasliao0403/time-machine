import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Copy, Check } from "lucide-react";

interface JsonModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  content: any;
  subtitle?: string;
}

const JsonModal: React.FC<JsonModalProps> = ({
  isOpen,
  onClose,
  title,
  content,
  subtitle,
}) => {
  const [copied, setCopied] = React.useState(false);

  const formattedContent =
    typeof content === "string" ? content : JSON.stringify(content, null, 2);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(formattedContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy content:", err);
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 overflow-auto"
          onClick={handleBackdropClick}
        >
          {/* Backdrop */}
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" />

          {/* Centered Container */}
          <div className="fixed inset-0 flex items-center justify-center p-4 pointer-events-none">
            {/* Re-enable pointer events for the modal content */}
            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-4xl max-h-[90vh] apple-glass-card border border-gray-300/20 rounded-xl overflow-hidden pointer-events-auto"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-300/20">
                <div>
                  <h2 className="text-xl font-semibold text-gray-100">
                    {title}
                  </h2>
                  {subtitle && (
                    <p className="text-gray-300 text-sm mt-1">{subtitle}</p>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleCopy}
                    className="p-2 rounded-lg text-gray-400 hover:text-gray-300 hover:bg-gray-300/10 transition-all"
                    title="Copy to clipboard"
                  >
                    {copied ? (
                      <Check className="h-5 w-5 text-green-400" />
                    ) : (
                      <Copy className="h-5 w-5" />
                    )}
                  </button>
                  <button
                    onClick={onClose}
                    className="p-2 rounded-lg text-gray-400 hover:text-gray-300 hover:bg-gray-300/10 transition-all"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="p-6 overflow-auto max-h-[calc(90vh-120px)]">
                <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono leading-relaxed bg-gray-900/50 p-4 rounded-lg border border-gray-300/10">
                  {formattedContent}
                </pre>
              </div>
            </motion.div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default JsonModal;
