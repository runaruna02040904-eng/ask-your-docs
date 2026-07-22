import { motion } from "framer-motion";
import type { ElementType, ReactNode } from "react";

interface FadeInProps {
  as?: ElementType;
  delay?: number;
  duration?: number;
  x?: number;
  y?: number;
  className?: string;
  children: ReactNode;
}

export default function FadeIn({
  as: Tag = "div",
  delay = 0,
  duration = 0.7,
  x = 0,
  y = 30,
  className = "",
  children,
}: FadeInProps) {
  const MotionTag = motion.create(Tag as any);
  return (
    <MotionTag
      initial={{ opacity: 0, x, y }}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
      viewport={{ once: true, margin: "50px", amount: 0 }}
      transition={{ duration, delay, ease: [0.25, 0.1, 0.25, 1] }}
      className={className}
    >
      {children}
    </MotionTag>
  );
}
