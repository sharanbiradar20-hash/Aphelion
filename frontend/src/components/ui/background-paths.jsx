import { motion } from 'framer-motion';

/**
 * FloatingPaths — Animated SVG paths that float across the background.
 * Adapted from 21st.dev BackgroundPaths (Ibelick) for CRA + JSX.
 */
function FloatingPaths({ position }) {
    const paths = Array.from({ length: 36 }, (_, i) => ({
        id: i,
        d: `M-${380 - i * 5 * position} -${189 + i * 6}C-${380 - i * 5 * position
            } -${189 + i * 6} -${312 - i * 5 * position} ${216 - i * 6} ${152 - i * 5 * position
            } ${343 - i * 6}C${616 - i * 5 * position} ${470 - i * 6} ${684 - i * 5 * position
            } ${875 - i * 6} ${684 - i * 5 * position} ${875 - i * 6}`,
        width: 0.5 + i * 0.03,
    }));

    return (
        <div className="absolute inset-0 pointer-events-none">
            <svg
                className="w-full h-full text-cyan-400"
                viewBox="0 0 696 316"
                fill="none"
            >
                <title>Background Paths</title>
                {paths.map((path) => (
                    <motion.path
                        key={path.id}
                        d={path.d}
                        stroke="currentColor"
                        strokeWidth={path.width}
                        strokeOpacity={0.03 + path.id * 0.008}
                        initial={{ pathLength: 0.3, opacity: 0.6 }}
                        animate={{
                            pathLength: 1,
                            opacity: [0.3, 0.6, 0.3],
                            pathOffset: [0, 1, 0],
                        }}
                        transition={{
                            duration: 20 + Math.random() * 10,
                            repeat: Infinity,
                            ease: 'linear',
                        }}
                    />
                ))}
            </svg>
        </div>
    );
}

/**
 * BackgroundPaths — Full background layer with animated floating SVG paths.
 *
 * Usage:
 *   <BackgroundPaths />                          — as a standalone background
 *   <BackgroundPaths>{children}</BackgroundPaths> — wraps content with the animated bg
 */
export function BackgroundPaths({ children }) {
    return (
        <div className="absolute inset-0 overflow-hidden pointer-events-none" style={{ zIndex: 0 }}>
            <FloatingPaths position={1} />
            <FloatingPaths position={-1} />
            {children}
        </div>
    );
}

export default BackgroundPaths;
