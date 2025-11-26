'use client'

import { motion } from "framer-motion"
import { useInView } from "react-intersection-observer"

export function AnimatedSection({ children }: { children: React.ReactNode }) {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.1,
  })

  return (
    <motion.section
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: inView ? 1 : 0, y: inView ? 0 : 50 }}
      transition={{ duration: 0.5 }}
    >
      {children}
    </motion.section>
  )
}
