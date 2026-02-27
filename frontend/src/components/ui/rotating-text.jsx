import { cn } from '../../lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect, useCallback } from 'react';

/**
 * RotatingText — Animated text rotator with 5 animation modes.
 * Adapted from 21st.dev (ErdaArt) for CRA + JSX.
 *
 * Props:
 *   words: string[]       — Array of words to cycle through
 *   interval?: number     — Time between rotations in ms (default: 2500)
 *   mode?: string         — Animation mode: "slide" | "fade" | "blur" | "flip" | "drop"
 *   className?: string    — Additional CSS classes
 */

const animations = {
    slide: {
        initial: { y: '100%', opacity: 0 },
        animate: { y: '0%', opacity: 1 },
        exit: { y: '-100%', opacity: 0 },
    },
    fade: {
        initial: { opacity: 0 },
        animate: { opacity: 1 },
        exit: { opacity: 0 },
    },
    blur: {
        initial: { opacity: 0, filter: 'blur(12px)' },
        animate: { opacity: 1, filter: 'blur(0px)' },
        exit: { opacity: 0, filter: 'blur(12px)' },
    },
    flip: {
        initial: { rotateX: 90, opacity: 0 },
        animate: { rotateX: 0, opacity: 1 },
        exit: { rotateX: -90, opacity: 0 },
    },
    drop: {
        initial: { y: '-80%', opacity: 0, scale: 0.8 },
        animate: { y: '0%', opacity: 1, scale: 1 },
        exit: { y: '80%', opacity: 0, scale: 0.8 },
    },
};

export function RotatingText({
    words,
    interval = 2500,
    mode = 'slide',
    className,
}) {
    const [index, setIndex] = useState(0);

    const next = useCallback(() => {
        setIndex((i) => (i + 1) % words.length);
    }, [words.length]);

    useEffect(() => {
        const id = setInterval(next, interval);
        return () => clearInterval(id);
    }, [next, interval]);

    const { initial, animate, exit } = animations[mode];

    return (
        <span
            className={cn('relative inline-flex overflow-hidden', className)}
            style={{ perspective: mode === 'flip' ? 600 : undefined }}
        >
            {/* Invisible placeholder to reserve width for the longest word */}
            <span className="invisible">
                {words.reduce((a, b) => (a.length > b.length ? a : b), '')}
            </span>

            <AnimatePresence mode="wait">
                <motion.span
                    key={words[index]}
                    className="absolute inset-0 flex items-center justify-center"
                    initial={initial}
                    animate={animate}
                    exit={exit}
                    transition={{
                        duration: 0.5,
                        ease: [0.32, 0.72, 0, 1],
                    }}
                >
                    {words[index]}
                </motion.span>
            </AnimatePresence>
        </span>
    );
}

export default RotatingText;
